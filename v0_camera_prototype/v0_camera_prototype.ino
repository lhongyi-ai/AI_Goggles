/*
  V0 Smart Glasses Camera Prototype
  Board: Seeed Studio XIAO ESP32S3 Sense

  V0 behavior:
  - Short press D1: save one JPEG photo to microSD.
  - Long press D1 for at least 1 second: save JPEG frames for 10 seconds.
  - External red LED on D2 stays on while capturing.
  - Files are numbered so old captures are not overwritten.

  Wiring:
  - D1 -> push button -> GND
  - D2 -> 330 ohm resistor -> LED anode; LED cathode -> GND

  Recommended board options:
  - Board: XIAO_ESP32S3
  - USB CDC On Boot: Enabled
  - PSRAM: OPI PSRAM
  - Partition Scheme: Maximum APP
*/

#include <Arduino.h>
#include "esp_camera.h"
#include "FS.h"
#include "SD.h"
#include "SPI.h"

// ============================================================
// User settings
// ============================================================

constexpr int BUTTON_PIN = D1;
constexpr int RECORD_LED_PIN = D2;

constexpr unsigned long DEBOUNCE_MS = 40;
constexpr unsigned long LONG_PRESS_MS = 1000;

constexpr unsigned long CLIP_DURATION_MS = 10000;
constexpr unsigned long FRAME_INTERVAL_MS = 100;

constexpr framesize_t CAMERA_FRAME_SIZE = FRAMESIZE_QVGA;
constexpr int JPEG_QUALITY = 15;

constexpr int SD_CS_PIN = 21;
constexpr int SD_SCK_PIN = D8;
constexpr int SD_MISO_PIN = D9;
constexpr int SD_MOSI_PIN = D10;
constexpr uint32_t SD_SPI_FREQUENCY = 10000000;

// ============================================================
// XIAO ESP32S3 Sense camera pin mapping
// ============================================================

constexpr int PWDN_GPIO_NUM = -1;
constexpr int RESET_GPIO_NUM = -1;
constexpr int XCLK_GPIO_NUM = 10;
constexpr int SIOD_GPIO_NUM = 40;
constexpr int SIOC_GPIO_NUM = 39;

constexpr int Y9_GPIO_NUM = 48;
constexpr int Y8_GPIO_NUM = 11;
constexpr int Y7_GPIO_NUM = 12;
constexpr int Y6_GPIO_NUM = 14;
constexpr int Y5_GPIO_NUM = 16;
constexpr int Y4_GPIO_NUM = 18;
constexpr int Y3_GPIO_NUM = 17;
constexpr int Y2_GPIO_NUM = 15;

constexpr int VSYNC_GPIO_NUM = 38;
constexpr int HREF_GPIO_NUM = 47;
constexpr int PCLK_GPIO_NUM = 13;

// ============================================================
// Global state
// ============================================================

uint32_t nextPhotoIndex = 1;
uint32_t nextClipIndex = 1;

bool buttonWasPressed = false;
bool longPressTriggered = false;

unsigned long buttonPressStartMs = 0;
unsigned long lastButtonChangeMs = 0;

int lastRawButtonState = HIGH;
int stableButtonState = HIGH;


// ============================================================
// Status LED helpers
// ============================================================

void setRecordingLed(bool on) {
  digitalWrite(RECORD_LED_PIN, on ? HIGH : LOW);
}

void blinkRecordingLed(int blinkCount, unsigned long onTimeMs, unsigned long offTimeMs) {
  for (int i = 0; i < blinkCount; ++i) {
    setRecordingLed(true);
    delay(onTimeMs);
    setRecordingLed(false);
    delay(offTimeMs);
  }
}

void fatalBlink(int blinkCount, unsigned long onTimeMs, unsigned long offTimeMs) {
  while (true) {
    blinkRecordingLed(blinkCount, onTimeMs, offTimeMs);
    delay(700);
  }
}

// ============================================================
// Camera initialization
// ============================================================

bool initializeCamera() {
  camera_config_t config;

  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;

  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;

  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;

  config.pin_sccb_sda = SIOD_GPIO_NUM;
  config.pin_sccb_scl = SIOC_GPIO_NUM;

  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;

  config.xclk_freq_hz = 20000000;
  config.pixel_format = PIXFORMAT_JPEG;

  config.frame_size = CAMERA_FRAME_SIZE;
  config.jpeg_quality = JPEG_QUALITY;
  config.fb_count = 2;
  config.grab_mode = CAMERA_GRAB_LATEST;
  config.fb_location = CAMERA_FB_IN_PSRAM;

  if (!psramFound()) {
    Serial.println("ERROR: PSRAM was not detected. Enable OPI PSRAM in board options.");
    config.frame_size = FRAMESIZE_QVGA;
    config.jpeg_quality = 15;
    config.fb_count = 1;
    config.fb_location = CAMERA_FB_IN_DRAM;
  }

  esp_err_t result = esp_camera_init(&config);
  if (result != ESP_OK) {
    Serial.printf("ERROR: Camera initialization failed. Error code: 0x%X\n", result);
    return false;
  }

  sensor_t *sensor = esp_camera_sensor_get();
  if (sensor == nullptr) {
    Serial.println("ERROR: Camera sensor was not found.");
    return false;
  }

  sensor->set_brightness(sensor, 0);
  sensor->set_contrast(sensor, 0);
  sensor->set_saturation(sensor, 0);

  Serial.println("Camera initialized successfully.");
  return true;
}

// ============================================================
// microSD initialization
// ============================================================

bool initializeMicroSD() {
  SPI.begin(SD_SCK_PIN, SD_MISO_PIN, SD_MOSI_PIN, SD_CS_PIN);

  if (!SD.begin(SD_CS_PIN, SPI, SD_SPI_FREQUENCY)) {
    Serial.println("ERROR: microSD card initialization failed.");
    Serial.println("Check card insertion and FAT32 formatting.");
    return false;
  }

  uint8_t cardType = SD.cardType();
  if (cardType == CARD_NONE) {
    Serial.println("ERROR: No microSD card detected.");
    return false;
  }

  uint64_t cardSizeMB = SD.cardSize() / (1024ULL * 1024ULL);
  Serial.printf("microSD initialized successfully. Capacity: %llu MB\n", cardSizeMB);

  File testFile = SD.open("/v0_boot_test.txt", FILE_WRITE);
  if (testFile) {
    testFile.println("V0 boot test");
    testFile.close();
    Serial.println("microSD write check passed: /v0_boot_test.txt");
  } else {
    Serial.println("WARNING: microSD mounted, but /v0_boot_test.txt could not be written.");
  }

  return true;
}

// ============================================================
// Filename management
// ============================================================

String makePhotoPath(uint32_t index) {
  char path[32];
  snprintf(path, sizeof(path), "/photo_%04lu.jpg", static_cast<unsigned long>(index));
  return String(path);
}

String makeClipDirectory(uint32_t index) {
  char path[24];
  snprintf(path, sizeof(path), "/clip_%04lu", static_cast<unsigned long>(index));
  return String(path);
}

String makeFramePath(const String &clipDirectory, uint32_t frameIndex) {
  char frameName[32];
  snprintf(frameName, sizeof(frameName), "/frame_%04lu.jpg", static_cast<unsigned long>(frameIndex));
  return clipDirectory + String(frameName);
}

void findNextAvailableIndexes() {
  nextPhotoIndex = 1;
  while (SD.exists(makePhotoPath(nextPhotoIndex).c_str())) {
    ++nextPhotoIndex;
  }

  nextClipIndex = 1;
  while (SD.exists(makeClipDirectory(nextClipIndex).c_str())) {
    ++nextClipIndex;
  }

  Serial.printf("Next photo index: %lu\n", static_cast<unsigned long>(nextPhotoIndex));
  Serial.printf("Next clip index: %lu\n", static_cast<unsigned long>(nextClipIndex));
}

// ============================================================
// Image capture and SD writing
// ============================================================

bool captureAndSaveJpeg(const String &filePath) {
  camera_fb_t *oldFrame = esp_camera_fb_get();
  if (oldFrame != nullptr) {
    esp_camera_fb_return(oldFrame);
  }

  camera_fb_t *frame = esp_camera_fb_get();
  if (frame == nullptr) {
    Serial.println("ERROR: Failed to capture camera frame.");
    return false;
  }

  if (frame->format != PIXFORMAT_JPEG) {
    Serial.println("ERROR: Captured frame is not JPEG.");
    esp_camera_fb_return(frame);
    return false;
  }

  File imageFile = SD.open(filePath.c_str(), FILE_WRITE);
  if (!imageFile) {
    Serial.printf("ERROR: Could not open %s for writing.\n", filePath.c_str());
    esp_camera_fb_return(frame);
    return false;
  }

  size_t bytesWritten = imageFile.write(frame->buf, frame->len);
  imageFile.flush();
  imageFile.close();

  size_t expectedBytes = frame->len;
  esp_camera_fb_return(frame);

  if (bytesWritten != expectedBytes) {
    Serial.printf(
      "ERROR: Incomplete write for %s. Wrote %u of %u bytes.\n",
      filePath.c_str(),
      static_cast<unsigned int>(bytesWritten),
      static_cast<unsigned int>(expectedBytes)
    );

    SD.remove(filePath.c_str());
    return false;
  }

  Serial.printf("Saved: %s (%u bytes)\n", filePath.c_str(), static_cast<unsigned int>(bytesWritten));
  return true;
}

bool captureAndSaveFastJpeg(const String &filePath) {
  camera_fb_t *frame = esp_camera_fb_get();
  if (frame == nullptr) {
    Serial.println("ERROR: Failed to capture camera frame.");
    return false;
  }

  if (frame->format != PIXFORMAT_JPEG) {
    Serial.println("ERROR: Captured frame is not JPEG.");
    esp_camera_fb_return(frame);
    return false;
  }

  File imageFile = SD.open(filePath.c_str(), FILE_WRITE);
  if (!imageFile) {
    Serial.printf("ERROR: Could not open %s for writing.\n", filePath.c_str());
    esp_camera_fb_return(frame);
    return false;
  }

  size_t bytesWritten = imageFile.write(frame->buf, frame->len);
  imageFile.close();

  size_t expectedBytes = frame->len;
  esp_camera_fb_return(frame);

  if (bytesWritten != expectedBytes) {
    SD.remove(filePath.c_str());
    return false;
  }

  return true;
}

// ============================================================
// Capture modes
// ============================================================

void takeSinglePhoto() {
  Serial.println();
  Serial.println("Single-photo mode started.");

  setRecordingLed(true);
  String photoPath = makePhotoPath(nextPhotoIndex);
  bool success = captureAndSaveJpeg(photoPath);
  setRecordingLed(false);

  if (success) {
    ++nextPhotoIndex;
    Serial.println("Single photo completed.");
    delay(100);
    blinkRecordingLed(1, 100, 0);
  } else {
    Serial.println("Single photo failed.");
    blinkRecordingLed(3, 100, 100);
  }
}

void recordJpegSequence() {
  Serial.println();
  Serial.println("Starting 10-second JPEG sequence.");
  Serial.printf(
    "Target frame interval: %lu ms (~%.2f FPS)\n",
    static_cast<unsigned long>(FRAME_INTERVAL_MS),
    1000.0f / static_cast<float>(FRAME_INTERVAL_MS)
  );

  String clipDirectory = makeClipDirectory(nextClipIndex);
  if (!SD.mkdir(clipDirectory.c_str())) {
    Serial.printf("ERROR: Could not create directory %s\n", clipDirectory.c_str());
    blinkRecordingLed(3, 150, 150);
    return;
  }

  Serial.printf("Saving frames in: %s\n", clipDirectory.c_str());
  setRecordingLed(true);

  unsigned long recordingStartMs = millis();
  unsigned long nextFrameTimeMs = recordingStartMs;
  uint32_t frameIndex = 1;
  uint32_t successfulFrames = 0;
  uint32_t failedFrames = 0;

  while (millis() - recordingStartMs < CLIP_DURATION_MS) {
    unsigned long currentTimeMs = millis();

    if (static_cast<long>(currentTimeMs - nextFrameTimeMs) >= 0) {
      String framePath = makeFramePath(clipDirectory, frameIndex);

      if (captureAndSaveFastJpeg(framePath)) {
        ++successfulFrames;
      } else {
        ++failedFrames;
      }

      ++frameIndex;
      nextFrameTimeMs += FRAME_INTERVAL_MS;

      if (static_cast<long>(millis() - nextFrameTimeMs) > static_cast<long>(FRAME_INTERVAL_MS)) {
        nextFrameTimeMs = millis() + FRAME_INTERVAL_MS;
      }
    }

    delay(1);
  }

  setRecordingLed(false);

  unsigned long recordingEndMs = millis();
  unsigned long elapsedMs = recordingEndMs - recordingStartMs;
  float elapsedSeconds = static_cast<float>(elapsedMs) / 1000.0f;
  float actualFps = elapsedSeconds > 0.0f
    ? static_cast<float>(successfulFrames) / elapsedSeconds
    : 0.0f;

  Serial.println();
  Serial.println("Recording finished: 10-second JPEG sequence completed.");
  Serial.printf("Elapsed time: %.2f seconds\n", elapsedSeconds);
  Serial.printf("Successful frames: %lu\n", static_cast<unsigned long>(successfulFrames));
  Serial.printf("Failed frames: %lu\n", static_cast<unsigned long>(failedFrames));
  Serial.printf("Actual FPS: %.2f\n", actualFps);
  Serial.printf("Saved folder: %s\n", clipDirectory.c_str());
  Serial.println("Convert on your computer with:");
  Serial.printf("ffmpeg -framerate %.0f -i %s/frame_%%04d.jpg -c:v libx264 -pix_fmt yuv420p output.mp4\n", actualFps, clipDirectory.c_str());

  ++nextClipIndex;

  if (successfulFrames >= 30) {
    blinkRecordingLed(2, 120, 100);
  } else if (successfulFrames > 0) {
    Serial.println("WARNING: Fewer than 30 frames captured. Try a faster SD card or lower JPEG quality/resolution.");
    blinkRecordingLed(3, 120, 100);
  } else {
    blinkRecordingLed(4, 100, 100);
  }
}

// ============================================================
// Controls
// ============================================================

void printHelp() {
  Serial.println();
  Serial.println("Commands:");
  Serial.println("  p - take one photo");
  Serial.println("  r - record one 10-second JPEG sequence");
  Serial.println("  s - print next file indexes");
  Serial.println("  h - print this help");
}

void updateSerialCommands() {
  while (Serial.available() > 0) {
    char command = static_cast<char>(Serial.read());

    if (command == 'p' || command == 'P') {
      takeSinglePhoto();
    } else if (command == 'r' || command == 'R') {
      recordJpegSequence();
    } else if (command == 's' || command == 'S') {
      Serial.printf("Next photo index: %lu\n", static_cast<unsigned long>(nextPhotoIndex));
      Serial.printf("Next clip index: %lu\n", static_cast<unsigned long>(nextClipIndex));
    } else if (command == 'h' || command == 'H' || command == '?') {
      printHelp();
    }
  }
}

void updateButton() {
  int rawButtonState = digitalRead(BUTTON_PIN);
  unsigned long currentTimeMs = millis();

  if (rawButtonState != lastRawButtonState) {
    lastButtonChangeMs = currentTimeMs;
    lastRawButtonState = rawButtonState;
  }

  if (currentTimeMs - lastButtonChangeMs >= DEBOUNCE_MS && rawButtonState != stableButtonState) {
    stableButtonState = rawButtonState;

    if (stableButtonState == LOW) {
      buttonWasPressed = true;
      longPressTriggered = false;
      buttonPressStartMs = currentTimeMs;
      Serial.println("Button pressed.");
    }

    if (stableButtonState == HIGH && buttonWasPressed) {
      unsigned long pressDurationMs = currentTimeMs - buttonPressStartMs;
      Serial.printf("Button released after %lu ms.\n", pressDurationMs);

      if (!longPressTriggered) {
        takeSinglePhoto();
      }

      buttonWasPressed = false;
      longPressTriggered = false;
    }
  }

  if (
    buttonWasPressed &&
    !longPressTriggered &&
    stableButtonState == LOW &&
    currentTimeMs - buttonPressStartMs >= LONG_PRESS_MS
  ) {
    longPressTriggered = true;
    Serial.println("Long press detected.");
    recordJpegSequence();

    buttonWasPressed = false;
    stableButtonState = digitalRead(BUTTON_PIN);
    lastRawButtonState = stableButtonState;
    lastButtonChangeMs = millis();
  }
}

// ============================================================
// Startup
// ============================================================

void setup() {
  pinMode(BUTTON_PIN, INPUT_PULLUP);
  pinMode(RECORD_LED_PIN, OUTPUT);
  setRecordingLed(false);

  Serial.begin(115200);

  unsigned long serialWaitStartMs = millis();
  while (!Serial && millis() - serialWaitStartMs < 5000) {
    delay(10);
  }

  Serial.println();
  Serial.println("========================================");
  Serial.println("V0 Smart Glasses Camera Prototype");
  Serial.println("XIAO ESP32S3 Sense");
  Serial.println("========================================");

  Serial.println("Initializing camera...");
  if (!initializeCamera()) {
    Serial.println("FATAL ERROR: Camera could not start.");
    fatalBlink(1, 100, 900);
  }

  Serial.println("Initializing microSD card...");
  if (!initializeMicroSD()) {
    Serial.println("FATAL ERROR: microSD could not start.");
    fatalBlink(2, 150, 350);
  }

  findNextAvailableIndexes();

  stableButtonState = digitalRead(BUTTON_PIN);
  lastRawButtonState = stableButtonState;
  lastButtonChangeMs = millis();

  Serial.println();
  Serial.println("System ready.");
  Serial.println("Short press: take one photo.");
  Serial.println("Long press: record a 10-second JPEG sequence.");
  printHelp();

  blinkRecordingLed(3, 150, 150);
}

void loop() {
  updateSerialCommands();
  updateButton();
  delay(2);
}
