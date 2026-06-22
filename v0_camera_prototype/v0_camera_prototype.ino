/*
  AI_Goggles V0 camera prototype
  Board: Seeed Studio XIAO ESP32S3 Sense

  Controls:
  - p: take one JPEG photo
  - r: start SD MJPEG recording while Wi-Fi preview remains available
  - x: stop the current SD recording
  - j: start JPEG sequence debug recording
  - m: start SD MJPEG recording
  - v: toggle the Wi-Fi preview server
  - w: print Wi-Fi status and preview URLs
  - s: print next file indexes
  - i: print hardware, memory, SD, and profile info
  - b: run the video smoothness benchmark suite
  - h: print help

  BLE exposes the same single-character commands through device AI_Goggles.
*/

#include <Arduino.h>
#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEUtils.h>
#include <WiFi.h>
#include <math.h>
#include <stdlib.h>
#include "esp_camera.h"
#include "esp_timer.h"
#include "FS.h"
#include "SD.h"
#include "SPI.h"

#if __has_include("wifi_config.h")
#include "wifi_config.h"
#endif

#ifndef WIFI_SSID
#define WIFI_SSID ""
#endif

#ifndef WIFI_PASSWORD
#define WIFI_PASSWORD ""
#endif

// ============================================================
// User-facing hardware settings
// ============================================================

constexpr int BUTTON_PIN = D1;
constexpr int RECORD_LED_PIN = D2;

constexpr unsigned long DEBOUNCE_MS = 40;
constexpr unsigned long LONG_PRESS_MS = 1000;

constexpr int SD_CS_PIN = 21;
constexpr int SD_SCK_PIN = D8;
constexpr int SD_MISO_PIN = D9;
constexpr int SD_MOSI_PIN = D10;
constexpr uint32_t SD_SAFE_FREQUENCY = 10000000;

constexpr const char *BLE_DEVICE_NAME = "AI_Goggles";
constexpr const char *BLE_SERVICE_UUID = "7b8f0001-2f5d-4d5a-9e4f-7f6a8c8d0001";
constexpr const char *BLE_CONTROL_UUID = "7b8f0002-2f5d-4d5a-9e4f-7f6a8c8d0001";

constexpr size_t MAX_TIMING_FRAMES = 1400;
constexpr uint32_t MIN_FREE_SD_BYTES = 2UL * 1024UL * 1024UL;
constexpr uint16_t HTTP_PORT = 80;
constexpr uint32_t WIFI_CONNECT_TIMEOUT_MS = 12000;
constexpr uint16_t PREVIEW_TARGET_FPS = 10;
constexpr uint8_t PREVIEW_FRAME_DIVIDER = 1;

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
// Recording profiles
// ============================================================

enum class StorageMode {
  SEPARATE_JPEG,
  MJPEG_SINGLE_FILE
};

enum class RecordingState {
  IDLE,
  RECORDING_MJPEG,
  RECORDING_JPEG_SEQUENCE,
  STOPPING,
  ERROR
};

struct RecordingProfile {
  const char *name;
  framesize_t frameSize;
  uint16_t width;
  uint16_t height;
  int jpegQuality;
  uint16_t targetFps;
  uint32_t sdFrequency;
  uint16_t durationSeconds;
  StorageMode storageMode;
  camera_grab_mode_t grabMode;
};

constexpr RecordingProfile PROFILES[] = {
  {"A_QVGA_Q15_10FPS_SD10_JPEG", FRAMESIZE_QVGA, 320, 240, 15, 10, 10000000, 10, StorageMode::SEPARATE_JPEG, CAMERA_GRAB_LATEST},
  {"B_QVGA_Q15_15FPS_SD20_JPEG", FRAMESIZE_QVGA, 320, 240, 15, 15, 20000000, 6, StorageMode::SEPARATE_JPEG, CAMERA_GRAB_LATEST},
  {"C_QVGA_Q20_20FPS_SD20_JPEG", FRAMESIZE_QVGA, 320, 240, 20, 20, 20000000, 6, StorageMode::SEPARATE_JPEG, CAMERA_GRAB_LATEST},
  {"D_VGA_Q15_10FPS_SD20_JPEG", FRAMESIZE_VGA, 640, 480, 15, 10, 20000000, 6, StorageMode::SEPARATE_JPEG, CAMERA_GRAB_LATEST},
  {"E_QVGA_Q15_10FPS_SD20_MJPEG", FRAMESIZE_QVGA, 320, 240, 15, 10, 20000000, 10, StorageMode::MJPEG_SINGLE_FILE, CAMERA_GRAB_LATEST},
};

constexpr size_t PROFILE_COUNT = sizeof(PROFILES) / sizeof(PROFILES[0]);
constexpr size_t RECOMMENDED_PROFILE_INDEX = 4;
constexpr size_t JPEG_SEQUENCE_PROFILE_INDEX = 0;

// ============================================================
// Recording measurements
// ============================================================

struct FrameTiming {
  uint32_t captureAttempt;
  uint32_t savedFrameIndex;
  uint64_t scheduledStartUs;
  uint64_t captureStartUs;
  uint64_t frameReadyUs;
  uint32_t captureDurationUs;
  uint32_t sdOpenDurationUs;
  uint32_t sdWriteDurationUs;
  uint32_t sdCloseDurationUs;
  uint32_t previewSendDurationUs;
  uint32_t totalFrameDurationUs;
  uint32_t frameIntervalUs;
  uint32_t jpegSizeBytes;
  bool writeSuccess;
  bool previewSent;
  bool previewDropped;
  bool deadlineMissed;
};

struct RecordingSummary {
  char profileName[40];
  char outputPath[64];
  uint16_t width = 0;
  uint16_t height = 0;
  int jpegQuality = 0;
  uint16_t targetFps = 0;
  uint32_t targetIntervalUs = 0;
  uint32_t requestedSdFrequency = 0;
  uint32_t actualSdFrequency = 0;
  StorageMode storageMode = StorageMode::SEPARATE_JPEG;
  uint16_t durationSeconds = 0;
  uint64_t recordingStartUs = 0;
  uint64_t recordingEndUs = 0;
  uint32_t captureAttempts = 0;
  uint32_t successfulFrames = 0;
  uint32_t failedFrames = 0;
  uint32_t previewFramesSent = 0;
  uint32_t previewFramesDropped = 0;
  uint32_t previewDisconnects = 0;
  uint32_t missedDeadlines = 0;
  uint32_t skippedFrameSlots = 0;
  uint32_t timingRowsStored = 0;
  bool timingTruncated = false;
  bool bleConnected = false;
  uint32_t freeHeapBefore = 0;
  uint32_t freeHeapAfter = 0;
  uint32_t freePsramBefore = 0;
  uint32_t freePsramAfter = 0;
  uint64_t totalBytesWritten = 0;
  uint32_t minJpegBytes = 0;
  uint32_t maxJpegBytes = 0;
  double actualFps = 0.0;
  double avgFrameIntervalUs = 0.0;
  uint32_t minFrameIntervalUs = 0;
  uint32_t maxFrameIntervalUs = 0;
  double stddevFrameIntervalUs = 0.0;
  uint32_t p50FrameIntervalUs = 0;
  uint32_t p95FrameIntervalUs = 0;
  uint32_t p99FrameIntervalUs = 0;
  double avgCaptureUs = 0.0;
  uint32_t p95CaptureUs = 0;
  double avgSdOpenUs = 0.0;
  double avgSdWriteUs = 0.0;
  uint32_t p95SdWriteUs = 0;
  double avgPreviewSendUs = 0.0;
  uint32_t p95PreviewSendUs = 0;
  double avgSdCloseUs = 0.0;
  double avgTotalFrameUs = 0.0;
  double avgJpegBytes = 0.0;
  double throughputKBps = 0.0;
  uint32_t longestStallUs = 0;
  uint64_t sdTotalBytes = 0;
  uint64_t sdUsedBytes = 0;
  uint64_t sdFreeBytes = 0;
};

struct CaptureWriteResult {
  bool success = false;
  uint32_t jpegSizeBytes = 0;
  uint32_t captureDurationUs = 0;
  uint32_t sdOpenDurationUs = 0;
  uint32_t sdWriteDurationUs = 0;
  uint32_t sdCloseDurationUs = 0;
  uint32_t previewSendDurationUs = 0;
  uint64_t captureStartUs = 0;
  uint64_t frameReadyUs = 0;
  bool previewSent = false;
  bool previewDropped = false;
};

struct RecordingSession {
  RecordingState state = RecordingState::IDLE;
  RecordingProfile profile = PROFILES[RECOMMENDED_PROFILE_INDEX];
  RecordingSummary summary;
  File mjpegFile;
  char infoPath[64] = {0};
  char timingPath[64] = {0};
  uint64_t previousCaptureStartUs = 0;
  uint64_t nextFrameDueUs = 0;
  uint32_t savedFrameIndex = 1;
  uint32_t theoreticalFrameSlot = 0;
  uint32_t consecutiveFailures = 0;
  uint32_t previewFramesSentAtStart = 0;
  uint32_t previewFramesDroppedAtStart = 0;
  uint32_t previewDisconnectsAtStart = 0;
  bool fileOpen = false;
};

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

BLECharacteristic *bleControlCharacteristic = nullptr;
volatile char pendingBleCommand = '\0';
volatile bool hasPendingBleCommand = false;
bool bleClientConnected = false;

FrameTiming *frameTimings = nullptr;
size_t frameTimingCapacity = MAX_TIMING_FRAMES;
static uint32_t metricScratch[MAX_TIMING_FRAMES];

bool cameraInitialized = false;
bool sdInitialized = false;
framesize_t activeFrameSize = FRAMESIZE_QVGA;
int activeJpegQuality = 15;
camera_grab_mode_t activeGrabMode = CAMERA_GRAB_LATEST;
uint32_t activeSdFrequency = SD_SAFE_FREQUENCY;

RecordingSummary lastBenchmarkSummaries[PROFILE_COUNT];
RecordingSession recordingSession;

WiFiServer httpServer(HTTP_PORT);
WiFiClient previewClient;
bool wifiConfigured = strlen(WIFI_SSID) > 0;
bool wifiConnected = false;
bool previewServerEnabled = true;
bool httpServerStarted = false;
uint32_t previewFramesSent = 0;
uint32_t previewFramesDropped = 0;
uint32_t previewDisconnects = 0;
uint64_t lastPreviewOnlyFrameUs = 0;
uint64_t lastStatusPrintUs = 0;

// ============================================================
// Forward declarations
// ============================================================

void setBleStatus(const String &status);
void queueBleCommand(char command);
void executeCommand(char command, const char *source);
bool recordClip(const RecordingProfile &profile, const char *reason, RecordingSummary *summaryOut);
bool startRecordingSession(const RecordingProfile &profile, const char *reason);
void requestStopRecordingSession(const char *reason);
void updateRecordingSession();
void updatePreviewOnlyCapture();
bool initializeWiFiAndHttp();
void updateHttpServer();
void printWiFiStatus();

class GogglesServerCallbacks : public BLEServerCallbacks {
  void onConnect(BLEServer *server) override {
    (void)server;
    bleClientConnected = true;
    Serial.println("BLE client connected.");
    setBleStatus("connected: write p,r,x,j,m,v,w,s,i,b,h");
  }

  void onDisconnect(BLEServer *server) override {
    bleClientConnected = false;
    Serial.println("BLE client disconnected; advertising restarted.");
    server->startAdvertising();
  }
};

class GogglesControlCallbacks : public BLECharacteristicCallbacks {
  void onWrite(BLECharacteristic *characteristic) override {
    String value = characteristic->getValue();
    if (value.length() > 0) {
      queueBleCommand(value[0]);
    }
  }
};

// ============================================================
// Utility helpers
// ============================================================

uint64_t nowUs() {
  return static_cast<uint64_t>(esp_timer_get_time());
}

const char *storageModeName(StorageMode mode) {
  return mode == StorageMode::SEPARATE_JPEG ? "separate_jpeg" : "mjpeg_single_file";
}

const char *recordingStateName(RecordingState state) {
  switch (state) {
    case RecordingState::IDLE:
      return "idle";
    case RecordingState::RECORDING_MJPEG:
      return "recording_mjpeg";
    case RecordingState::RECORDING_JPEG_SEQUENCE:
      return "recording_jpeg_sequence";
    case RecordingState::STOPPING:
      return "stopping";
    case RecordingState::ERROR:
      return "error";
  }
  return "unknown";
}

const char *grabModeName(camera_grab_mode_t mode) {
  return mode == CAMERA_GRAB_LATEST ? "latest" : "when_empty";
}

bool isRecordingActive() {
  return recordingSession.state == RecordingState::RECORDING_MJPEG ||
         recordingSession.state == RecordingState::RECORDING_JPEG_SEQUENCE ||
         recordingSession.state == RecordingState::STOPPING;
}

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

uint32_t estimateRequiredBytes(const RecordingProfile &profile) {
  uint32_t targetFrames = profile.durationSeconds * profile.targetFps;
  uint32_t roughBytesPerFrame = (static_cast<uint32_t>(profile.width) * profile.height) / 4;
  return targetFrames * roughBytesPerFrame + 1024UL * 1024UL;
}

bool loadSdSpace(RecordingSummary *summary) {
  if (!sdInitialized) {
    return false;
  }

  uint64_t totalBytes = SD.totalBytes();
  uint64_t usedBytes = SD.usedBytes();
  uint64_t freeBytes = totalBytes > usedBytes ? totalBytes - usedBytes : 0;

  if (summary != nullptr) {
    summary->sdTotalBytes = totalBytes;
    summary->sdUsedBytes = usedBytes;
    summary->sdFreeBytes = freeBytes;
  }

  Serial.printf("SD total: %llu MB\n", totalBytes / (1024ULL * 1024ULL));
  Serial.printf("SD used: %llu MB\n", usedBytes / (1024ULL * 1024ULL));
  Serial.printf("SD free: %llu MB\n", freeBytes / (1024ULL * 1024ULL));

  return true;
}

// ============================================================
// Camera and SD initialization
// ============================================================

bool initializeCameraForProfile(const RecordingProfile &profile) {
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
  config.frame_size = profile.frameSize;
  config.jpeg_quality = profile.jpegQuality;
  config.fb_count = 2;
  config.grab_mode = profile.grabMode;
  config.fb_location = CAMERA_FB_IN_PSRAM;

  if (!psramFound()) {
    Serial.println("ERROR: PSRAM was not detected. Enable OPI PSRAM in board options.");
    config.frame_size = FRAMESIZE_QVGA;
    config.jpeg_quality = 20;
    config.fb_count = 1;
    config.fb_location = CAMERA_FB_IN_DRAM;
  }

  esp_err_t result = esp_camera_init(&config);
  if (result != ESP_OK) {
    Serial.printf("ERROR: Camera initialization failed. Error code: 0x%X\n", result);
    cameraInitialized = false;
    return false;
  }

  sensor_t *sensor = esp_camera_sensor_get();
  if (sensor == nullptr) {
    Serial.println("ERROR: Camera sensor was not found.");
    cameraInitialized = false;
    return false;
  }

  sensor->set_brightness(sensor, 0);
  sensor->set_contrast(sensor, 0);
  sensor->set_saturation(sensor, 0);

  activeFrameSize = profile.frameSize;
  activeJpegQuality = profile.jpegQuality;
  activeGrabMode = profile.grabMode;
  cameraInitialized = true;

  Serial.printf("Camera ready: %s, %ux%u, JPEG quality %d, grab %s\n",
                profile.name, profile.width, profile.height, profile.jpegQuality, grabModeName(profile.grabMode));
  return true;
}

bool ensureCameraForProfile(const RecordingProfile &profile) {
  if (cameraInitialized &&
      activeFrameSize == profile.frameSize &&
      activeJpegQuality == profile.jpegQuality &&
      activeGrabMode == profile.grabMode) {
    return true;
  }

  if (cameraInitialized) {
    esp_camera_deinit();
    cameraInitialized = false;
    delay(100);
  }

  return initializeCameraForProfile(profile);
}

bool mountMicroSD(uint32_t frequency) {
  if (sdInitialized) {
    SD.end();
    sdInitialized = false;
    delay(20);
  }

  SPI.begin(SD_SCK_PIN, SD_MISO_PIN, SD_MOSI_PIN, SD_CS_PIN);

  if (!SD.begin(SD_CS_PIN, SPI, frequency)) {
    Serial.printf("ERROR: microSD init failed at %lu Hz.\n", static_cast<unsigned long>(frequency));
    return false;
  }

  if (SD.cardType() == CARD_NONE) {
    Serial.println("ERROR: No microSD card detected.");
    SD.end();
    return false;
  }

  activeSdFrequency = frequency;
  sdInitialized = true;
  Serial.printf("microSD mounted at %lu Hz.\n", static_cast<unsigned long>(frequency));
  loadSdSpace(nullptr);
  return true;
}

bool ensureSdFrequency(uint32_t requestedFrequency, uint32_t *actualFrequency) {
  if (sdInitialized && activeSdFrequency == requestedFrequency) {
    if (actualFrequency != nullptr) {
      *actualFrequency = activeSdFrequency;
    }
    return true;
  }

  if (mountMicroSD(requestedFrequency)) {
    if (actualFrequency != nullptr) {
      *actualFrequency = requestedFrequency;
    }
    return true;
  }

  if (requestedFrequency != SD_SAFE_FREQUENCY) {
    Serial.println("Falling back to 10 MHz SD SPI.");
    if (mountMicroSD(SD_SAFE_FREQUENCY)) {
      if (actualFrequency != nullptr) {
        *actualFrequency = SD_SAFE_FREQUENCY;
      }
      return true;
    }
  }

  return false;
}

// ============================================================
// BLE control
// ============================================================

void setBleStatus(const String &status) {
  if (bleControlCharacteristic != nullptr) {
    bleControlCharacteristic->setValue(status);
  }
}

void queueBleCommand(char command) {
  if (command >= 'A' && command <= 'Z') {
    command = static_cast<char>(command - 'A' + 'a');
  }

  if (command != 'p' && command != 'r' && command != 'x' && command != 'j' && command != 'm' &&
      command != 'v' && command != 'w' && command != 's' && command != 'h' && command != 'i' && command != 'b') {
    setBleStatus("error: write p,r,x,j,m,v,w,s,i,b,h");
    Serial.printf("BLE ignored unknown command: %c\n", command);
    return;
  }

  pendingBleCommand = command;
  hasPendingBleCommand = true;
  setBleStatus(String("queued: ") + command);
  Serial.printf("BLE queued command: %c\n", command);
}

bool initializeBLE() {
  if (!BLEDevice::init(BLE_DEVICE_NAME)) {
    Serial.println("WARNING: BLE initialization failed.");
    return false;
  }

  BLEServer *server = BLEDevice::createServer();
  server->setCallbacks(new GogglesServerCallbacks());
  server->advertiseOnDisconnect(true);

  BLEService *service = server->createService(BLE_SERVICE_UUID);
  bleControlCharacteristic = service->createCharacteristic(
    BLE_CONTROL_UUID,
    BLECharacteristic::PROPERTY_READ | BLECharacteristic::PROPERTY_WRITE
  );
  bleControlCharacteristic->setCallbacks(new GogglesControlCallbacks());
  setBleStatus("ready: write p,r,x,j,m,v,w,s,i,b,h");

  service->start();

  BLEAdvertising *advertising = BLEDevice::getAdvertising();
  advertising->addServiceUUID(BLE_SERVICE_UUID);
  advertising->setScanResponse(true);
  advertising->setMinPreferred(0x06);
  advertising->setMaxPreferred(0x12);
  BLEDevice::startAdvertising();

  Serial.println("BLE control ready.");
  Serial.printf("BLE device name: %s\n", BLE_DEVICE_NAME);
  Serial.printf("BLE service UUID: %s\n", BLE_SERVICE_UUID);
  Serial.printf("BLE control UUID: %s\n", BLE_CONTROL_UUID);
  return true;
}

// ============================================================
// Filename management
// ============================================================

void makePhotoPath(uint32_t index, char *path, size_t pathSize) {
  snprintf(path, pathSize, "/photo_%04lu.jpg", static_cast<unsigned long>(index));
}

void makeClipDirectory(uint32_t index, char *path, size_t pathSize) {
  snprintf(path, pathSize, "/clip_%04lu", static_cast<unsigned long>(index));
}

void makeFramePath(const char *clipDirectory, uint32_t frameIndex, char *path, size_t pathSize) {
  snprintf(path, pathSize, "%s/frame_%04lu.jpg", clipDirectory, static_cast<unsigned long>(frameIndex));
}

void makeMjpegPath(uint32_t index, char *path, size_t pathSize) {
  snprintf(path, pathSize, "/clip_%04lu.mjpeg", static_cast<unsigned long>(index));
}

void makeMjpegInfoPath(uint32_t index, char *path, size_t pathSize) {
  snprintf(path, pathSize, "/clip_%04lu_info.csv", static_cast<unsigned long>(index));
}

void makeMjpegTimingPath(uint32_t index, char *path, size_t pathSize) {
  snprintf(path, pathSize, "/clip_%04lu_timing.csv", static_cast<unsigned long>(index));
}

bool clipIndexExists(uint32_t index) {
  if (!sdInitialized) {
    return false;
  }

  char path[64];
  makeClipDirectory(index, path, sizeof(path));
  if (SD.exists(path)) {
    return true;
  }
  makeMjpegPath(index, path, sizeof(path));
  if (SD.exists(path)) {
    return true;
  }
  makeMjpegInfoPath(index, path, sizeof(path));
  return SD.exists(path);
}

void findNextAvailableIndexes() {
  if (!sdInitialized) {
    Serial.println("microSD is not mounted; file indexes will be scanned after SD is available.");
    nextPhotoIndex = 1;
    nextClipIndex = 1;
    return;
  }

  char path[64];
  nextPhotoIndex = 1;
  makePhotoPath(nextPhotoIndex, path, sizeof(path));
  while (SD.exists(path)) {
    ++nextPhotoIndex;
    makePhotoPath(nextPhotoIndex, path, sizeof(path));
  }

  nextClipIndex = 1;
  while (clipIndexExists(nextClipIndex)) {
    ++nextClipIndex;
  }

  Serial.printf("Next photo index: %lu\n", static_cast<unsigned long>(nextPhotoIndex));
  Serial.printf("Next clip index: %lu\n", static_cast<unsigned long>(nextClipIndex));
}

// ============================================================
// Image capture and SD writing
// ============================================================

bool captureAndSaveJpeg(const char *filePath) {
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

  if (SD.exists(filePath)) {
    Serial.printf("ERROR: Refusing to append existing file %s\n", filePath);
    esp_camera_fb_return(frame);
    return false;
  }

  File imageFile = SD.open(filePath, FILE_WRITE);
  if (!imageFile) {
    Serial.printf("ERROR: Could not open %s for writing.\n", filePath);
    esp_camera_fb_return(frame);
    return false;
  }

  size_t bytesWritten = imageFile.write(frame->buf, frame->len);
  imageFile.close();

  size_t expectedBytes = frame->len;
  esp_camera_fb_return(frame);

  if (bytesWritten != expectedBytes) {
    Serial.printf("ERROR: Incomplete write for %s. Wrote %u of %u bytes.\n",
                  filePath, static_cast<unsigned int>(bytesWritten), static_cast<unsigned int>(expectedBytes));
    SD.remove(filePath);
    return false;
  }

  Serial.printf("Saved: %s (%u bytes)\n", filePath, static_cast<unsigned int>(bytesWritten));
  return true;
}

bool hasPreviewClient() {
  return previewClient && previewClient.connected();
}

void closePreviewClient(const char *reason) {
  if (previewClient) {
    previewClient.stop();
  }
  ++previewDisconnects;
  Serial.printf("Preview client disconnected: %s\n", reason);
}

bool sendAllToPreview(const uint8_t *data, size_t length) {
  if (!hasPreviewClient()) {
    return false;
  }

  size_t written = previewClient.write(data, length);
  if (written != length) {
    closePreviewClient("short write");
    return false;
  }

  return true;
}

bool sendTextToPreview(const char *text) {
  return sendAllToPreview(reinterpret_cast<const uint8_t *>(text), strlen(text));
}

bool sendPreviewFrame(camera_fb_t *frame, uint32_t *sendDurationUs, bool *dropped) {
  *sendDurationUs = 0;
  *dropped = false;

  if (!hasPreviewClient()) {
    return false;
  }

  char header[96];
  int headerLength = snprintf(
    header,
    sizeof(header),
    "--frame\r\nContent-Type: image/jpeg\r\nContent-Length: %u\r\n\r\n",
    static_cast<unsigned int>(frame->len)
  );

  int availableBytes = previewClient.availableForWrite();
  size_t requiredBytes = static_cast<size_t>(headerLength) + frame->len + 2;
  if (availableBytes > 0 && static_cast<size_t>(availableBytes) < min(requiredBytes, static_cast<size_t>(4096))) {
    *dropped = true;
    ++previewFramesDropped;
    return false;
  }

  uint64_t sendStartUs = nowUs();
  bool ok = sendAllToPreview(reinterpret_cast<const uint8_t *>(header), static_cast<size_t>(headerLength)) &&
            sendAllToPreview(frame->buf, frame->len) &&
            sendTextToPreview("\r\n");
  *sendDurationUs = static_cast<uint32_t>(nowUs() - sendStartUs);

  if (ok) {
    ++previewFramesSent;
  } else {
    *dropped = true;
    ++previewFramesDropped;
  }

  return ok;
}

CaptureWriteResult captureAndDistributeFrame(const char *filePath, File *mjpegFile, bool writeToSd, bool allowPreview) {
  CaptureWriteResult result;
  result.captureStartUs = nowUs();

  camera_fb_t *frame = esp_camera_fb_get();
  result.frameReadyUs = nowUs();
  result.captureDurationUs = static_cast<uint32_t>(result.frameReadyUs - result.captureStartUs);

  if (frame == nullptr) {
    return result;
  }

  if (frame->format != PIXFORMAT_JPEG) {
    esp_camera_fb_return(frame);
    return result;
  }

  result.jpegSizeBytes = frame->len;

  File imageFile;
  size_t bytesWritten = 0;
  size_t expectedBytes = frame->len;

  if (writeToSd) {
    uint64_t openStartUs = nowUs();
    if (mjpegFile == nullptr) {
      if (SD.exists(filePath)) {
        esp_camera_fb_return(frame);
        return result;
      }
      imageFile = SD.open(filePath, FILE_WRITE);
      result.sdOpenDurationUs = static_cast<uint32_t>(nowUs() - openStartUs);
      if (!imageFile) {
        esp_camera_fb_return(frame);
        return result;
      }
    } else {
      result.sdOpenDurationUs = 0;
    }

    File &targetFile = mjpegFile == nullptr ? imageFile : *mjpegFile;

    uint64_t writeStartUs = nowUs();
    bytesWritten = targetFile.write(frame->buf, frame->len);
    result.sdWriteDurationUs = static_cast<uint32_t>(nowUs() - writeStartUs);

    uint64_t closeStartUs = nowUs();
    if (mjpegFile == nullptr) {
      imageFile.close();
    }
    result.sdCloseDurationUs = static_cast<uint32_t>(nowUs() - closeStartUs);

    if (bytesWritten == expectedBytes) {
      result.success = true;
    } else if (mjpegFile == nullptr && filePath != nullptr) {
      SD.remove(filePath);
    }
  } else {
    result.success = true;
  }

  if (allowPreview) {
    result.previewSent = sendPreviewFrame(frame, &result.previewSendDurationUs, &result.previewDropped);
  }

  esp_camera_fb_return(frame);

  return result;
}

CaptureWriteResult captureAndWriteFrame(const char *filePath, File *mjpegFile) {
  return captureAndDistributeFrame(filePath, mjpegFile, true, false);
}

// ============================================================
// Statistics and CSV output
// ============================================================

int compareU32(const void *a, const void *b) {
  uint32_t left = *static_cast<const uint32_t *>(a);
  uint32_t right = *static_cast<const uint32_t *>(b);
  if (left < right) {
    return -1;
  }
  if (left > right) {
    return 1;
  }
  return 0;
}

uint32_t percentileFromScratch(size_t count, double percentile) {
  if (count == 0) {
    return 0;
  }
  qsort(metricScratch, count, sizeof(uint32_t), compareU32);
  double rank = (percentile / 100.0) * static_cast<double>(count - 1);
  size_t index = static_cast<size_t>(rank + 0.5);
  if (index >= count) {
    index = count - 1;
  }
  return metricScratch[index];
}

void computeMetricStats(uint32_t FrameTiming::*field, uint32_t rowCount, double *average, uint32_t *p95) {
  uint64_t sum = 0;
  size_t count = 0;

  for (uint32_t i = 0; i < rowCount && count < MAX_TIMING_FRAMES; ++i) {
    uint32_t value = frameTimings[i].*field;
    if (value == 0) {
      continue;
    }
    metricScratch[count++] = value;
    sum += value;
  }

  *average = count > 0 ? static_cast<double>(sum) / static_cast<double>(count) : 0.0;
  *p95 = percentileFromScratch(count, 95.0);
}

void computeSummaryStats(RecordingSummary &summary) {
  uint32_t intervalCount = 0;
  uint64_t intervalSum = 0;
  uint64_t intervalSquares = 0;
  summary.minFrameIntervalUs = UINT32_MAX;
  summary.maxFrameIntervalUs = 0;
  summary.minJpegBytes = UINT32_MAX;
  summary.maxJpegBytes = 0;
  summary.longestStallUs = 0;

  for (uint32_t i = 0; i < summary.timingRowsStored; ++i) {
    const FrameTiming &row = frameTimings[i];

    if (row.frameIntervalUs > 0 && intervalCount < MAX_TIMING_FRAMES) {
      metricScratch[intervalCount++] = row.frameIntervalUs;
      intervalSum += row.frameIntervalUs;
      intervalSquares += static_cast<uint64_t>(row.frameIntervalUs) * row.frameIntervalUs;
      summary.minFrameIntervalUs = min(summary.minFrameIntervalUs, row.frameIntervalUs);
      summary.maxFrameIntervalUs = max(summary.maxFrameIntervalUs, row.frameIntervalUs);
      summary.longestStallUs = max(summary.longestStallUs, row.frameIntervalUs);
    }

    if (row.writeSuccess && row.jpegSizeBytes > 0) {
      summary.minJpegBytes = min(summary.minJpegBytes, row.jpegSizeBytes);
      summary.maxJpegBytes = max(summary.maxJpegBytes, row.jpegSizeBytes);
    }
  }

  if (intervalCount == 0) {
    summary.minFrameIntervalUs = 0;
  } else {
    summary.avgFrameIntervalUs = static_cast<double>(intervalSum) / intervalCount;
    double meanSquares = static_cast<double>(intervalSquares) / intervalCount;
    double variance = meanSquares - summary.avgFrameIntervalUs * summary.avgFrameIntervalUs;
    summary.stddevFrameIntervalUs = variance > 0.0 ? sqrt(variance) : 0.0;
    summary.p50FrameIntervalUs = percentileFromScratch(intervalCount, 50.0);
    summary.p95FrameIntervalUs = percentileFromScratch(intervalCount, 95.0);
    summary.p99FrameIntervalUs = percentileFromScratch(intervalCount, 99.0);
  }

  computeMetricStats(&FrameTiming::captureDurationUs, summary.timingRowsStored, &summary.avgCaptureUs, &summary.p95CaptureUs);
  computeMetricStats(&FrameTiming::sdWriteDurationUs, summary.timingRowsStored, &summary.avgSdWriteUs, &summary.p95SdWriteUs);
  computeMetricStats(&FrameTiming::previewSendDurationUs, summary.timingRowsStored, &summary.avgPreviewSendUs, &summary.p95PreviewSendUs);

  uint64_t openSum = 0;
  uint64_t closeSum = 0;
  uint64_t totalFrameSum = 0;
  uint32_t openCount = 0;
  uint32_t closeCount = 0;
  uint32_t totalCount = 0;

  for (uint32_t i = 0; i < summary.timingRowsStored; ++i) {
    if (frameTimings[i].sdOpenDurationUs > 0) {
      openSum += frameTimings[i].sdOpenDurationUs;
      ++openCount;
    }
    if (frameTimings[i].sdCloseDurationUs > 0) {
      closeSum += frameTimings[i].sdCloseDurationUs;
      ++closeCount;
    }
    if (frameTimings[i].totalFrameDurationUs > 0) {
      totalFrameSum += frameTimings[i].totalFrameDurationUs;
      ++totalCount;
    }
  }

  summary.avgSdOpenUs = openCount > 0 ? static_cast<double>(openSum) / openCount : 0.0;
  summary.avgSdCloseUs = closeCount > 0 ? static_cast<double>(closeSum) / closeCount : 0.0;
  summary.avgTotalFrameUs = totalCount > 0 ? static_cast<double>(totalFrameSum) / totalCount : 0.0;

  if (summary.minJpegBytes == UINT32_MAX) {
    summary.minJpegBytes = 0;
  }

  double elapsedSeconds = (summary.recordingEndUs > summary.recordingStartUs)
    ? static_cast<double>(summary.recordingEndUs - summary.recordingStartUs) / 1000000.0
    : 0.0;
  summary.actualFps = elapsedSeconds > 0.0 ? static_cast<double>(summary.successfulFrames) / elapsedSeconds : 0.0;
  summary.avgJpegBytes = summary.successfulFrames > 0
    ? static_cast<double>(summary.totalBytesWritten) / summary.successfulFrames
    : 0.0;
  summary.throughputKBps = elapsedSeconds > 0.0
    ? static_cast<double>(summary.totalBytesWritten) / 1024.0 / elapsedSeconds
    : 0.0;
}

void printSummary(const RecordingSummary &summary) {
  double elapsedSeconds = (summary.recordingEndUs - summary.recordingStartUs) / 1000000.0;

  Serial.println();
  Serial.println("Recording summary");
  Serial.println("-----------------");
  Serial.printf("Profile: %s\n", summary.profileName);
  Serial.printf("Output: %s\n", summary.outputPath);
  Serial.printf("Resolution: %ux%u\n", summary.width, summary.height);
  Serial.printf("JPEG quality: %d\n", summary.jpegQuality);
  Serial.printf("Target FPS: %u\n", summary.targetFps);
  Serial.printf("Target interval: %lu us\n", static_cast<unsigned long>(summary.targetIntervalUs));
  Serial.printf("Duration: %.2f seconds\n", elapsedSeconds);
  Serial.printf("Storage mode: %s\n", storageModeName(summary.storageMode));
  Serial.printf("SD frequency requested/actual: %lu/%lu Hz\n",
                static_cast<unsigned long>(summary.requestedSdFrequency),
                static_cast<unsigned long>(summary.actualSdFrequency));
  Serial.printf("Capture attempts: %lu\n", static_cast<unsigned long>(summary.captureAttempts));
  Serial.printf("Successful frames: %lu\n", static_cast<unsigned long>(summary.successfulFrames));
  Serial.printf("Failed frames: %lu\n", static_cast<unsigned long>(summary.failedFrames));
  Serial.printf("Actual FPS: %.2f\n", summary.actualFps);
  Serial.printf("Interval avg/min/max/stddev: %.1f/%lu/%lu/%.1f us\n",
                summary.avgFrameIntervalUs,
                static_cast<unsigned long>(summary.minFrameIntervalUs),
                static_cast<unsigned long>(summary.maxFrameIntervalUs),
                summary.stddevFrameIntervalUs);
  Serial.printf("Interval P50/P95/P99: %lu/%lu/%lu us\n",
                static_cast<unsigned long>(summary.p50FrameIntervalUs),
                static_cast<unsigned long>(summary.p95FrameIntervalUs),
                static_cast<unsigned long>(summary.p99FrameIntervalUs));
  Serial.printf("Capture avg/P95: %.1f/%lu us\n",
                summary.avgCaptureUs, static_cast<unsigned long>(summary.p95CaptureUs));
  Serial.printf("SD open avg: %.1f us\n", summary.avgSdOpenUs);
  Serial.printf("SD write avg/P95: %.1f/%lu us\n",
                summary.avgSdWriteUs, static_cast<unsigned long>(summary.p95SdWriteUs));
  Serial.printf("SD close avg: %.1f us\n", summary.avgSdCloseUs);
  Serial.printf("Preview sent/dropped/disconnects: %lu/%lu/%lu\n",
                static_cast<unsigned long>(summary.previewFramesSent),
                static_cast<unsigned long>(summary.previewFramesDropped),
                static_cast<unsigned long>(summary.previewDisconnects));
  Serial.printf("Preview send avg/P95: %.1f/%lu us\n",
                summary.avgPreviewSendUs, static_cast<unsigned long>(summary.p95PreviewSendUs));
  Serial.printf("Total frame avg: %.1f us\n", summary.avgTotalFrameUs);
  Serial.printf("JPEG avg/min/max: %.1f/%lu/%lu bytes\n",
                summary.avgJpegBytes,
                static_cast<unsigned long>(summary.minJpegBytes),
                static_cast<unsigned long>(summary.maxJpegBytes));
  Serial.printf("Bytes written: %llu\n", summary.totalBytesWritten);
  Serial.printf("Effective SD throughput: %.1f KB/s\n", summary.throughputKBps);
  Serial.printf("Missed deadlines: %lu\n", static_cast<unsigned long>(summary.missedDeadlines));
  Serial.printf("Skipped theoretical frame slots: %lu\n", static_cast<unsigned long>(summary.skippedFrameSlots));
  Serial.printf("Longest stall: %lu us\n", static_cast<unsigned long>(summary.longestStallUs));
  Serial.printf("Timing rows stored: %lu%s\n",
                static_cast<unsigned long>(summary.timingRowsStored),
                summary.timingTruncated ? " (truncated)" : "");
  Serial.printf("Heap before/after: %lu/%lu bytes\n",
                static_cast<unsigned long>(summary.freeHeapBefore),
                static_cast<unsigned long>(summary.freeHeapAfter));
  Serial.printf("PSRAM before/after: %lu/%lu bytes\n",
                static_cast<unsigned long>(summary.freePsramBefore),
                static_cast<unsigned long>(summary.freePsramAfter));
  Serial.printf("BLE state: %s\n", summary.bleConnected ? "connected" : "disconnected");
}

void writeCsvLine(File &file, const char *key, const char *value) {
  file.print(key);
  file.print(',');
  file.println(value);
}

void writeCsvLineU32(File &file, const char *key, uint32_t value) {
  file.print(key);
  file.print(',');
  file.println(value);
}

void writeCsvLineU64(File &file, const char *key, uint64_t value) {
  file.print(key);
  file.print(',');
  file.println(value);
}

void writeCsvLineDouble(File &file, const char *key, double value, int digits = 3) {
  file.print(key);
  file.print(',');
  file.println(value, digits);
}

bool writeClipInfoCsv(const char *path, const RecordingSummary &summary) {
  File file = SD.open(path, FILE_WRITE);
  if (!file) {
    Serial.printf("ERROR: Could not write %s\n", path);
    return false;
  }

  file.println("key,value");
  writeCsvLine(file, "profile", summary.profileName);
  writeCsvLine(file, "output_path", summary.outputPath);
  writeCsvLine(file, "storage_mode", storageModeName(summary.storageMode));
  writeCsvLineU32(file, "width", summary.width);
  writeCsvLineU32(file, "height", summary.height);
  writeCsvLineU32(file, "jpeg_quality", summary.jpegQuality);
  writeCsvLineU32(file, "target_fps", summary.targetFps);
  writeCsvLineU32(file, "target_interval_us", summary.targetIntervalUs);
  writeCsvLineU32(file, "requested_sd_frequency", summary.requestedSdFrequency);
  writeCsvLineU32(file, "actual_sd_frequency", summary.actualSdFrequency);
  writeCsvLineU32(file, "duration_seconds", summary.durationSeconds);
  writeCsvLineU64(file, "recording_start_us", summary.recordingStartUs);
  writeCsvLineU64(file, "recording_end_us", summary.recordingEndUs);
  writeCsvLineU32(file, "capture_attempts", summary.captureAttempts);
  writeCsvLineU32(file, "successful_frames", summary.successfulFrames);
  writeCsvLineU32(file, "failed_frames", summary.failedFrames);
  writeCsvLineU32(file, "preview_frames_sent", summary.previewFramesSent);
  writeCsvLineU32(file, "preview_frames_dropped", summary.previewFramesDropped);
  writeCsvLineU32(file, "preview_disconnects", summary.previewDisconnects);
  writeCsvLineDouble(file, "actual_average_fps", summary.actualFps);
  writeCsvLineDouble(file, "average_frame_interval_us", summary.avgFrameIntervalUs);
  writeCsvLineU32(file, "minimum_frame_interval_us", summary.minFrameIntervalUs);
  writeCsvLineU32(file, "maximum_frame_interval_us", summary.maxFrameIntervalUs);
  writeCsvLineDouble(file, "frame_interval_stddev_us", summary.stddevFrameIntervalUs);
  writeCsvLineU32(file, "p50_frame_interval_us", summary.p50FrameIntervalUs);
  writeCsvLineU32(file, "p95_frame_interval_us", summary.p95FrameIntervalUs);
  writeCsvLineU32(file, "p99_frame_interval_us", summary.p99FrameIntervalUs);
  writeCsvLineDouble(file, "average_camera_capture_us", summary.avgCaptureUs);
  writeCsvLineU32(file, "p95_camera_capture_us", summary.p95CaptureUs);
  writeCsvLineDouble(file, "average_sd_open_us", summary.avgSdOpenUs);
  writeCsvLineDouble(file, "average_sd_write_us", summary.avgSdWriteUs);
  writeCsvLineU32(file, "p95_sd_write_us", summary.p95SdWriteUs);
  writeCsvLineDouble(file, "average_preview_send_us", summary.avgPreviewSendUs);
  writeCsvLineU32(file, "p95_preview_send_us", summary.p95PreviewSendUs);
  writeCsvLineDouble(file, "average_sd_close_us", summary.avgSdCloseUs);
  writeCsvLineDouble(file, "average_total_frame_us", summary.avgTotalFrameUs);
  writeCsvLineDouble(file, "average_jpeg_size_bytes", summary.avgJpegBytes);
  writeCsvLineU32(file, "minimum_jpeg_size_bytes", summary.minJpegBytes);
  writeCsvLineU32(file, "maximum_jpeg_size_bytes", summary.maxJpegBytes);
  writeCsvLineU64(file, "total_bytes_written", summary.totalBytesWritten);
  writeCsvLineDouble(file, "effective_sd_throughput_kb_s", summary.throughputKBps);
  writeCsvLineU32(file, "missed_deadlines", summary.missedDeadlines);
  writeCsvLineU32(file, "skipped_theoretical_frame_slots", summary.skippedFrameSlots);
  writeCsvLineU32(file, "longest_stall_us", summary.longestStallUs);
  writeCsvLineU32(file, "free_internal_heap_before", summary.freeHeapBefore);
  writeCsvLineU32(file, "free_internal_heap_after", summary.freeHeapAfter);
  writeCsvLineU32(file, "free_psram_before", summary.freePsramBefore);
  writeCsvLineU32(file, "free_psram_after", summary.freePsramAfter);
  writeCsvLine(file, "ble_state", summary.bleConnected ? "connected" : "disconnected");
  writeCsvLineU64(file, "sd_total_bytes", summary.sdTotalBytes);
  writeCsvLineU64(file, "sd_used_bytes", summary.sdUsedBytes);
  writeCsvLineU64(file, "sd_free_bytes", summary.sdFreeBytes);
  writeCsvLine(file, "timing_truncated", summary.timingTruncated ? "true" : "false");
  file.close();
  return true;
}

bool writeFrameTimingCsv(const char *path, const RecordingSummary &summary) {
  File file = SD.open(path, FILE_WRITE);
  if (!file) {
    Serial.printf("ERROR: Could not write %s\n", path);
    return false;
  }

  file.println("capture_attempt,saved_frame_index,scheduled_start_us,capture_start_us,frame_ready_us,capture_duration_us,sd_open_duration_us,sd_write_duration_us,sd_close_duration_us,preview_send_duration_us,total_frame_duration_us,frame_interval_us,jpeg_size_bytes,write_success,preview_sent,preview_dropped,deadline_missed");

  for (uint32_t i = 0; i < summary.timingRowsStored; ++i) {
    const FrameTiming &row = frameTimings[i];
    file.printf("%lu,%lu,%llu,%llu,%llu,%lu,%lu,%lu,%lu,%lu,%lu,%lu,%lu,%u,%u,%u,%u\n",
                static_cast<unsigned long>(row.captureAttempt),
                static_cast<unsigned long>(row.savedFrameIndex),
                row.scheduledStartUs,
                row.captureStartUs,
                row.frameReadyUs,
                static_cast<unsigned long>(row.captureDurationUs),
                static_cast<unsigned long>(row.sdOpenDurationUs),
                static_cast<unsigned long>(row.sdWriteDurationUs),
                static_cast<unsigned long>(row.sdCloseDurationUs),
                static_cast<unsigned long>(row.previewSendDurationUs),
                static_cast<unsigned long>(row.totalFrameDurationUs),
                static_cast<unsigned long>(row.frameIntervalUs),
                static_cast<unsigned long>(row.jpegSizeBytes),
                row.writeSuccess ? 1 : 0,
                row.previewSent ? 1 : 0,
                row.previewDropped ? 1 : 0,
                row.deadlineMissed ? 1 : 0);
  }

  file.close();
  return true;
}

// ============================================================
// Capture modes
// ============================================================

void takeSinglePhoto() {
  if (!ensureCameraForProfile(PROFILES[RECOMMENDED_PROFILE_INDEX])) {
    Serial.println("Single photo failed: camera not ready.");
    blinkRecordingLed(3, 100, 100);
    return;
  }

  Serial.println();
  Serial.println("Single-photo mode started.");
  setRecordingLed(true);

  char photoPath[64];
  makePhotoPath(nextPhotoIndex, photoPath, sizeof(photoPath));
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

bool prepareClipOutputs(const RecordingProfile &profile, uint32_t clipIndex, char *outputPath, size_t outputSize, char *infoPath, size_t infoSize, char *timingPath, size_t timingSize) {
  if (profile.storageMode == StorageMode::SEPARATE_JPEG) {
    makeClipDirectory(clipIndex, outputPath, outputSize);
    snprintf(infoPath, infoSize, "%s/clip_info.csv", outputPath);
    snprintf(timingPath, timingSize, "%s/frame_timing.csv", outputPath);

    if (SD.exists(outputPath)) {
      return false;
    }
    return SD.mkdir(outputPath);
  }

  makeMjpegPath(clipIndex, outputPath, outputSize);
  makeMjpegInfoPath(clipIndex, infoPath, infoSize);
  makeMjpegTimingPath(clipIndex, timingPath, timingSize);

  if (SD.exists(outputPath) || SD.exists(infoPath) || SD.exists(timingPath)) {
    return false;
  }

  return true;
}

bool recordClip(const RecordingProfile &profile, const char *reason, RecordingSummary *summaryOut) {
  RecordingSummary summary;
  strlcpy(summary.profileName, profile.name, sizeof(summary.profileName));
  summary.width = profile.width;
  summary.height = profile.height;
  summary.jpegQuality = profile.jpegQuality;
  summary.targetFps = profile.targetFps;
  summary.targetIntervalUs = 1000000UL / profile.targetFps;
  summary.requestedSdFrequency = profile.sdFrequency;
  summary.storageMode = profile.storageMode;
  summary.durationSeconds = profile.durationSeconds;
  summary.bleConnected = bleClientConnected;

  Serial.println();
  Serial.printf("Starting recording: %s (%s)\n", profile.name, reason);

  if (!ensureCameraForProfile(profile)) {
    Serial.println("ERROR: Camera profile could not be applied.");
    return false;
  }

  if (!ensureSdFrequency(profile.sdFrequency, &summary.actualSdFrequency)) {
    Serial.println("ERROR: microSD is not available.");
    return false;
  }

  loadSdSpace(&summary);
  uint32_t estimatedBytes = estimateRequiredBytes(profile);
  if (summary.sdFreeBytes < MIN_FREE_SD_BYTES || summary.sdFreeBytes < estimatedBytes) {
    Serial.printf("ERROR: Refusing to record. SD free bytes %llu, estimated need %lu.\n",
                  summary.sdFreeBytes, static_cast<unsigned long>(estimatedBytes));
    return false;
  }

  while (clipIndexExists(nextClipIndex)) {
    ++nextClipIndex;
  }

  char infoPath[64];
  char timingPath[64];
  if (!prepareClipOutputs(profile, nextClipIndex, summary.outputPath, sizeof(summary.outputPath), infoPath, sizeof(infoPath), timingPath, sizeof(timingPath))) {
    Serial.printf("ERROR: Could not create output for clip index %lu.\n", static_cast<unsigned long>(nextClipIndex));
    return false;
  }

  File mjpegFile;
  if (profile.storageMode == StorageMode::MJPEG_SINGLE_FILE) {
    mjpegFile = SD.open(summary.outputPath, FILE_WRITE);
    if (!mjpegFile) {
      Serial.printf("ERROR: Could not create %s\n", summary.outputPath);
      return false;
    }
  }

  summary.freeHeapBefore = ESP.getFreeHeap();
  summary.freePsramBefore = ESP.getFreePsram();
  summary.recordingStartUs = nowUs();
  uint64_t previousCaptureStartUs = 0;
  uint32_t savedFrameIndex = 1;
  uint32_t consecutiveFailures = 0;
  uint32_t theoreticalFrameSlot = 0;

  setRecordingLed(true);

  while (nowUs() - summary.recordingStartUs < static_cast<uint64_t>(profile.durationSeconds) * 1000000ULL) {
    uint64_t scheduledStartUs = summary.recordingStartUs + static_cast<uint64_t>(theoreticalFrameSlot) * summary.targetIntervalUs;
    uint64_t currentUs = nowUs();

    if (currentUs < scheduledStartUs) {
      uint64_t waitUs = scheduledStartUs - currentUs;
      if (waitUs > 2000) {
        delay(static_cast<uint32_t>(waitUs / 1000));
      } else if (waitUs > 50) {
        delayMicroseconds(static_cast<uint32_t>(waitUs));
      }
    }

    currentUs = nowUs();
    bool deadlineMissed = currentUs > scheduledStartUs + summary.targetIntervalUs;
    if (deadlineMissed) {
      ++summary.missedDeadlines;
    }

    ++summary.captureAttempts;
    char framePath[72] = {0};
    if (profile.storageMode == StorageMode::SEPARATE_JPEG) {
      makeFramePath(summary.outputPath, savedFrameIndex, framePath, sizeof(framePath));
    }

    CaptureWriteResult result = captureAndWriteFrame(
      profile.storageMode == StorageMode::SEPARATE_JPEG ? framePath : nullptr,
      profile.storageMode == StorageMode::MJPEG_SINGLE_FILE ? &mjpegFile : nullptr
    );
    uint64_t frameEndUs = nowUs();

    if (summary.timingRowsStored < frameTimingCapacity && frameTimings != nullptr) {
      FrameTiming &row = frameTimings[summary.timingRowsStored++];
      row.captureAttempt = summary.captureAttempts;
      row.savedFrameIndex = result.success ? savedFrameIndex : 0;
      row.scheduledStartUs = scheduledStartUs;
      row.captureStartUs = result.captureStartUs;
      row.frameReadyUs = result.frameReadyUs;
      row.captureDurationUs = result.captureDurationUs;
      row.sdOpenDurationUs = result.sdOpenDurationUs;
      row.sdWriteDurationUs = result.sdWriteDurationUs;
      row.sdCloseDurationUs = result.sdCloseDurationUs;
      row.previewSendDurationUs = result.previewSendDurationUs;
      row.totalFrameDurationUs = result.captureStartUs > 0 ? static_cast<uint32_t>(frameEndUs - result.captureStartUs) : 0;
      row.frameIntervalUs = previousCaptureStartUs > 0 && result.captureStartUs > previousCaptureStartUs
        ? static_cast<uint32_t>(result.captureStartUs - previousCaptureStartUs)
        : 0;
      row.jpegSizeBytes = result.jpegSizeBytes;
      row.writeSuccess = result.success;
      row.previewSent = result.previewSent;
      row.previewDropped = result.previewDropped;
      row.deadlineMissed = deadlineMissed;
    } else {
      summary.timingTruncated = true;
    }

    if (result.captureStartUs > 0) {
      previousCaptureStartUs = result.captureStartUs;
    }

    if (result.success) {
      ++summary.successfulFrames;
      summary.totalBytesWritten += result.jpegSizeBytes;
      ++savedFrameIndex;
      consecutiveFailures = 0;
    } else {
      ++summary.failedFrames;
      ++consecutiveFailures;
      if (consecutiveFailures >= 8) {
        Serial.println("ERROR: Too many consecutive frame write failures; stopping clip.");
        break;
      }
    }

    ++theoreticalFrameSlot;
    uint64_t nextSlotTime = summary.recordingStartUs + static_cast<uint64_t>(theoreticalFrameSlot) * summary.targetIntervalUs;
    uint64_t afterFrameUs = nowUs();
    while (afterFrameUs > nextSlotTime + summary.targetIntervalUs) {
      ++theoreticalFrameSlot;
      ++summary.skippedFrameSlots;
      nextSlotTime = summary.recordingStartUs + static_cast<uint64_t>(theoreticalFrameSlot) * summary.targetIntervalUs;
    }

    delay(1);
  }

  setRecordingLed(false);

  if (profile.storageMode == StorageMode::MJPEG_SINGLE_FILE) {
    mjpegFile.flush();
    mjpegFile.close();
  }

  summary.recordingEndUs = nowUs();
  summary.freeHeapAfter = ESP.getFreeHeap();
  summary.freePsramAfter = ESP.getFreePsram();
  computeSummaryStats(summary);
  printSummary(summary);

  writeClipInfoCsv(infoPath, summary);
  writeFrameTimingCsv(timingPath, summary);

  ++nextClipIndex;

  if (summary.failedFrames > 0 && summary.actualSdFrequency > SD_SAFE_FREQUENCY) {
    Serial.println("Write failures occurred at high SD frequency; falling back to 10 MHz for future operations.");
    mountMicroSD(SD_SAFE_FREQUENCY);
    findNextAvailableIndexes();
  }

  if (summary.successfulFrames > 0) {
    blinkRecordingLed(summary.failedFrames == 0 ? 2 : 3, 120, 100);
  } else {
    blinkRecordingLed(4, 100, 100);
  }

  if (summaryOut != nullptr) {
    *summaryOut = summary;
  }

  return summary.successfulFrames > 0;
}

bool startRecordingSession(const RecordingProfile &profile, const char *reason) {
  if (isRecordingActive()) {
    Serial.println("ERROR: A recording session is already active. Send x to stop it first.");
    setBleStatus("error: already recording");
    return false;
  }

  RecordingSession session;
  session.state = profile.storageMode == StorageMode::MJPEG_SINGLE_FILE
    ? RecordingState::RECORDING_MJPEG
    : RecordingState::RECORDING_JPEG_SEQUENCE;
  session.profile = profile;

  RecordingSummary &summary = session.summary;
  strlcpy(summary.profileName, profile.name, sizeof(summary.profileName));
  summary.width = profile.width;
  summary.height = profile.height;
  summary.jpegQuality = profile.jpegQuality;
  summary.targetFps = profile.targetFps;
  summary.targetIntervalUs = 1000000UL / profile.targetFps;
  summary.requestedSdFrequency = profile.sdFrequency;
  summary.storageMode = profile.storageMode;
  summary.durationSeconds = 0;
  summary.bleConnected = bleClientConnected;

  Serial.println();
  Serial.printf("Starting live recording session: %s (%s)\n", profile.name, reason);

  if (!ensureCameraForProfile(profile)) {
    Serial.println("ERROR: Camera profile could not be applied.");
    setBleStatus("error: camera");
    return false;
  }

  if (!ensureSdFrequency(profile.sdFrequency, &summary.actualSdFrequency)) {
    Serial.println("ERROR: microSD is not available.");
    setBleStatus("error: sd");
    return false;
  }

  loadSdSpace(&summary);
  if (summary.sdFreeBytes < MIN_FREE_SD_BYTES) {
    Serial.printf("ERROR: Refusing to record. SD free bytes %llu.\n", summary.sdFreeBytes);
    setBleStatus("error: sd free");
    return false;
  }

  while (clipIndexExists(nextClipIndex)) {
    ++nextClipIndex;
  }

  if (!prepareClipOutputs(profile, nextClipIndex, summary.outputPath, sizeof(summary.outputPath), session.infoPath, sizeof(session.infoPath), session.timingPath, sizeof(session.timingPath))) {
    Serial.printf("ERROR: Could not create output for clip index %lu.\n", static_cast<unsigned long>(nextClipIndex));
    setBleStatus("error: output");
    return false;
  }

  if (profile.storageMode == StorageMode::MJPEG_SINGLE_FILE) {
    session.mjpegFile = SD.open(summary.outputPath, FILE_WRITE);
    if (!session.mjpegFile) {
      Serial.printf("ERROR: Could not create %s\n", summary.outputPath);
      setBleStatus("error: mjpeg open");
      return false;
    }
    session.fileOpen = true;
  }

  summary.freeHeapBefore = ESP.getFreeHeap();
  summary.freePsramBefore = ESP.getFreePsram();
  summary.recordingStartUs = nowUs();
  session.nextFrameDueUs = summary.recordingStartUs;
  session.previewFramesSentAtStart = previewFramesSent;
  session.previewFramesDroppedAtStart = previewFramesDropped;
  session.previewDisconnectsAtStart = previewDisconnects;
  recordingSession = session;

  setRecordingLed(true);
  setBleStatus(profile.storageMode == StorageMode::MJPEG_SINGLE_FILE ? "recording: mjpeg" : "recording: jpeg");

  Serial.printf("Recording output: %s\n", recordingSession.summary.outputPath);
  Serial.println("Send x to stop and write metadata.");
  return true;
}

void finishRecordingSession(const char *reason) {
  if (recordingSession.state == RecordingState::IDLE) {
    return;
  }

  RecordingSummary &summary = recordingSession.summary;
  Serial.printf("Finishing recording session: %s\n", reason);

  if (recordingSession.fileOpen) {
    recordingSession.mjpegFile.flush();
    recordingSession.mjpegFile.close();
    recordingSession.fileOpen = false;
  }

  summary.recordingEndUs = nowUs();
  summary.freeHeapAfter = ESP.getFreeHeap();
  summary.freePsramAfter = ESP.getFreePsram();
  summary.previewFramesSent = previewFramesSent - recordingSession.previewFramesSentAtStart;
  summary.previewFramesDropped = previewFramesDropped - recordingSession.previewFramesDroppedAtStart;
  summary.previewDisconnects = previewDisconnects - recordingSession.previewDisconnectsAtStart;

  computeSummaryStats(summary);
  printSummary(summary);
  writeClipInfoCsv(recordingSession.infoPath, summary);
  writeFrameTimingCsv(recordingSession.timingPath, summary);

  ++nextClipIndex;
  setRecordingLed(false);

  if (summary.failedFrames > 0 && summary.actualSdFrequency > SD_SAFE_FREQUENCY) {
    Serial.println("Write failures occurred at high SD frequency; falling back to 10 MHz for future operations.");
    mountMicroSD(SD_SAFE_FREQUENCY);
    findNextAvailableIndexes();
  }

  setBleStatus("ready: recording stopped");
  recordingSession = RecordingSession();
}

void requestStopRecordingSession(const char *reason) {
  if (!isRecordingActive()) {
    Serial.println("No active recording session to stop.");
    setBleStatus("ready: idle");
    return;
  }

  Serial.printf("Stop requested: %s\n", reason);
  recordingSession.state = RecordingState::STOPPING;
}

void updateRecordingSession() {
  if (recordingSession.state == RecordingState::IDLE || recordingSession.state == RecordingState::ERROR) {
    return;
  }

  if (recordingSession.state == RecordingState::STOPPING) {
    finishRecordingSession("stop command");
    return;
  }

  RecordingSummary &summary = recordingSession.summary;
  uint64_t currentUs = nowUs();
  if (currentUs < recordingSession.nextFrameDueUs) {
    return;
  }

  bool deadlineMissed = currentUs > recordingSession.nextFrameDueUs + summary.targetIntervalUs;
  if (deadlineMissed) {
    ++summary.missedDeadlines;
  }

  ++summary.captureAttempts;
  char framePath[72] = {0};
  if (summary.storageMode == StorageMode::SEPARATE_JPEG) {
    makeFramePath(summary.outputPath, recordingSession.savedFrameIndex, framePath, sizeof(framePath));
  }

  CaptureWriteResult result = captureAndDistributeFrame(
    summary.storageMode == StorageMode::SEPARATE_JPEG ? framePath : nullptr,
    summary.storageMode == StorageMode::MJPEG_SINGLE_FILE ? &recordingSession.mjpegFile : nullptr,
    true,
    previewServerEnabled && hasPreviewClient() && (summary.captureAttempts % PREVIEW_FRAME_DIVIDER == 0)
  );
  uint64_t frameEndUs = nowUs();

  if (summary.timingRowsStored < frameTimingCapacity && frameTimings != nullptr) {
    FrameTiming &row = frameTimings[summary.timingRowsStored++];
    row.captureAttempt = summary.captureAttempts;
    row.savedFrameIndex = result.success ? recordingSession.savedFrameIndex : 0;
    row.scheduledStartUs = recordingSession.nextFrameDueUs;
    row.captureStartUs = result.captureStartUs;
    row.frameReadyUs = result.frameReadyUs;
    row.captureDurationUs = result.captureDurationUs;
    row.sdOpenDurationUs = result.sdOpenDurationUs;
    row.sdWriteDurationUs = result.sdWriteDurationUs;
    row.sdCloseDurationUs = result.sdCloseDurationUs;
    row.previewSendDurationUs = result.previewSendDurationUs;
    row.totalFrameDurationUs = result.captureStartUs > 0 ? static_cast<uint32_t>(frameEndUs - result.captureStartUs) : 0;
    row.frameIntervalUs = recordingSession.previousCaptureStartUs > 0 && result.captureStartUs > recordingSession.previousCaptureStartUs
      ? static_cast<uint32_t>(result.captureStartUs - recordingSession.previousCaptureStartUs)
      : 0;
    row.jpegSizeBytes = result.jpegSizeBytes;
    row.writeSuccess = result.success;
    row.previewSent = result.previewSent;
    row.previewDropped = result.previewDropped;
    row.deadlineMissed = deadlineMissed;
  } else {
    summary.timingTruncated = true;
  }

  if (result.captureStartUs > 0) {
    recordingSession.previousCaptureStartUs = result.captureStartUs;
  }

  if (result.success) {
    ++summary.successfulFrames;
    summary.totalBytesWritten += result.jpegSizeBytes;
    ++recordingSession.savedFrameIndex;
    recordingSession.consecutiveFailures = 0;
  } else {
    ++summary.failedFrames;
    ++recordingSession.consecutiveFailures;
    if (recordingSession.consecutiveFailures >= 8) {
      Serial.println("ERROR: Too many consecutive frame write failures; stopping clip.");
      recordingSession.state = RecordingState::STOPPING;
    }
  }

  ++recordingSession.theoreticalFrameSlot;
  recordingSession.nextFrameDueUs = summary.recordingStartUs + static_cast<uint64_t>(recordingSession.theoreticalFrameSlot) * summary.targetIntervalUs;
  uint64_t afterFrameUs = nowUs();
  while (afterFrameUs > recordingSession.nextFrameDueUs + summary.targetIntervalUs) {
    ++recordingSession.theoreticalFrameSlot;
    ++summary.skippedFrameSlots;
    recordingSession.nextFrameDueUs = summary.recordingStartUs + static_cast<uint64_t>(recordingSession.theoreticalFrameSlot) * summary.targetIntervalUs;
  }
}

void updatePreviewOnlyCapture() {
  if (isRecordingActive() || !previewServerEnabled || !hasPreviewClient()) {
    return;
  }

  if (!ensureCameraForProfile(PROFILES[RECOMMENDED_PROFILE_INDEX])) {
    closePreviewClient("camera unavailable");
    return;
  }

  uint64_t currentUs = nowUs();
  uint32_t intervalUs = 1000000UL / PREVIEW_TARGET_FPS;
  if (lastPreviewOnlyFrameUs != 0 && currentUs - lastPreviewOnlyFrameUs < intervalUs) {
    return;
  }

  CaptureWriteResult result = captureAndDistributeFrame(nullptr, nullptr, false, true);
  lastPreviewOnlyFrameUs = result.captureStartUs > 0 ? result.captureStartUs : currentUs;
}

void printBenchmarkTable(const RecordingSummary *summaries, size_t count) {
  Serial.println();
  Serial.println("Benchmark comparison");
  Serial.println("Profile,Resolution,Q,TargetFPS,SDMHz,Mode,ActualFPS,P95IntervalUs,AvgJpegBytes,ThroughputKBps,Failed,LongestStallUs,BLE");

  for (size_t i = 0; i < count; ++i) {
    const RecordingSummary &s = summaries[i];
    Serial.printf("%s,%ux%u,%d,%u,%lu,%s,%.2f,%lu,%.1f,%.1f,%lu,%lu,%s\n",
                  s.profileName,
                  s.width,
                  s.height,
                  s.jpegQuality,
                  s.targetFps,
                  static_cast<unsigned long>(s.actualSdFrequency / 1000000UL),
                  storageModeName(s.storageMode),
                  s.actualFps,
                  static_cast<unsigned long>(s.p95FrameIntervalUs),
                  s.avgJpegBytes,
                  s.throughputKBps,
                  static_cast<unsigned long>(s.failedFrames),
                  static_cast<unsigned long>(s.longestStallUs),
                  s.bleConnected ? "connected" : "disconnected");
  }
}

void runBenchmarkSuite() {
  Serial.println();
  Serial.println("Starting benchmark suite. Existing files will not be deleted.");
  setBleStatus("busy: benchmark");

  for (size_t i = 0; i < PROFILE_COUNT; ++i) {
    recordClip(PROFILES[i], "benchmark", &lastBenchmarkSummaries[i]);
    delay(2000);
  }

  printBenchmarkTable(lastBenchmarkSummaries, PROFILE_COUNT);
  setBleStatus("ready: benchmark done");
}

void printSystemInfo() {
  Serial.println();
  Serial.println("System info");
  Serial.println("-----------");
  Serial.println("Board: Seeed Studio XIAO ESP32S3 Sense");
  Serial.printf("PSRAM found: %s\n", psramFound() ? "yes" : "no");
  Serial.printf("Free internal heap: %lu bytes\n", static_cast<unsigned long>(ESP.getFreeHeap()));
  Serial.printf("Free PSRAM: %lu bytes\n", static_cast<unsigned long>(ESP.getFreePsram()));
  Serial.printf("Current SD frequency: %lu Hz\n", static_cast<unsigned long>(activeSdFrequency));
  Serial.printf("BLE: %s\n", bleClientConnected ? "connected" : "advertising/disconnected");
  Serial.printf("Recording state: %s\n", recordingStateName(recordingSession.state));
  Serial.printf("Wi-Fi: %s\n", wifiConnected ? WiFi.localIP().toString().c_str() : (wifiConfigured ? "configured, disconnected" : "not configured"));
  Serial.printf("Preview client: %s\n", hasPreviewClient() ? "connected" : "none");
  loadSdSpace(nullptr);

  Serial.println();
  Serial.println("Profiles:");
  for (size_t i = 0; i < PROFILE_COUNT; ++i) {
    const RecordingProfile &p = PROFILES[i];
    Serial.printf("%u: %s, %ux%u, Q%d, %u FPS, SD %lu MHz, %us, %s, grab=%s\n",
                  static_cast<unsigned int>(i),
                  p.name,
                  p.width,
                  p.height,
                  p.jpegQuality,
                  p.targetFps,
                  static_cast<unsigned long>(p.sdFrequency / 1000000UL),
                  p.durationSeconds,
                  storageModeName(p.storageMode),
                  grabModeName(p.grabMode));
  }
}

// ============================================================
// Wi-Fi preview server
// ============================================================

double currentSessionFps() {
  if (!isRecordingActive() || recordingSession.summary.recordingStartUs == 0) {
    return 0.0;
  }

  double elapsedSeconds = static_cast<double>(nowUs() - recordingSession.summary.recordingStartUs) / 1000000.0;
  return elapsedSeconds > 0.0 ? static_cast<double>(recordingSession.summary.successfulFrames) / elapsedSeconds : 0.0;
}

String httpUrl(const char *path) {
  if (!wifiConnected) {
    return String("Wi-Fi not connected");
  }
  return String("http://") + WiFi.localIP().toString() + path;
}

bool initializeWiFiAndHttp() {
  if (!wifiConfigured) {
    Serial.println("Wi-Fi SSID is not configured. Create v0_camera_prototype/wifi_config.h to enable preview.");
    return false;
  }

  WiFi.mode(WIFI_STA);
  WiFi.setSleep(false);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  Serial.printf("Connecting to Wi-Fi SSID: %s\n", WIFI_SSID);
  unsigned long startMs = millis();
  while (WiFi.status() != WL_CONNECTED && millis() - startMs < WIFI_CONNECT_TIMEOUT_MS) {
    delay(250);
    Serial.print('.');
  }
  Serial.println();

  wifiConnected = WiFi.status() == WL_CONNECTED;
  if (!wifiConnected) {
    Serial.println("WARNING: Wi-Fi did not connect. SD recording still works.");
    return false;
  }

  httpServer.begin();
  httpServerStarted = true;
  Serial.println("Wi-Fi preview server ready.");
  printWiFiStatus();
  return true;
}

void ensureWiFiConnection() {
  if (!wifiConfigured) {
    wifiConnected = false;
    return;
  }

  bool connectedNow = WiFi.status() == WL_CONNECTED;
  if (wifiConnected && !connectedNow) {
    Serial.println("WARNING: Wi-Fi disconnected. SD recording continues.");
    if (hasPreviewClient()) {
      closePreviewClient("wifi disconnected");
    }
  }

  wifiConnected = connectedNow;
}

void printWiFiStatus() {
  ensureWiFiConnection();

  Serial.println();
  Serial.println("Wi-Fi / Preview");
  Serial.println("----------------");
  Serial.printf("Configured: %s\n", wifiConfigured ? "yes" : "no");
  Serial.printf("Connected: %s\n", wifiConnected ? "yes" : "no");
  Serial.printf("Preview server: %s\n", previewServerEnabled ? "enabled" : "disabled");
  Serial.printf("HTTP server started: %s\n", httpServerStarted ? "yes" : "no");
  Serial.printf("Stream client: %s\n", hasPreviewClient() ? "connected" : "none");
  Serial.printf("Preview sent/dropped/disconnects: %lu/%lu/%lu\n",
                static_cast<unsigned long>(previewFramesSent),
                static_cast<unsigned long>(previewFramesDropped),
                static_cast<unsigned long>(previewDisconnects));
  if (wifiConnected) {
    Serial.printf("IP: %s\n", WiFi.localIP().toString().c_str());
    Serial.printf("Preview page: %s\n", httpUrl("/").c_str());
    Serial.printf("Stream URL: %s\n", httpUrl("/stream").c_str());
    Serial.printf("Status URL: %s\n", httpUrl("/status").c_str());
  } else if (!wifiConfigured) {
    Serial.println("Create v0_camera_prototype/wifi_config.h with WIFI_SSID and WIFI_PASSWORD.");
  }
}

String readHttpRequestLine(WiFiClient &client) {
  String line;
  unsigned long startMs = millis();
  while (client.connected() && millis() - startMs < 300) {
    while (client.available() > 0) {
      char c = static_cast<char>(client.read());
      if (c == '\n') {
        line.trim();
        return line;
      }
      if (c != '\r') {
        line += c;
      }
      if (line.length() > 160) {
        line.trim();
        return line;
      }
    }
    delay(1);
  }
  line.trim();
  return line;
}

void drainHttpHeaders(WiFiClient &client) {
  unsigned long startMs = millis();
  String line;
  while (client.connected() && millis() - startMs < 300) {
    while (client.available() > 0) {
      char c = static_cast<char>(client.read());
      if (c == '\n') {
        line.trim();
        if (line.length() == 0) {
          return;
        }
        line = "";
      } else if (c != '\r') {
        line += c;
      }
    }
    delay(1);
  }
}

void sendHttpHeader(WiFiClient &client, const char *status, const char *contentType, const char *extraHeaders = nullptr) {
  client.printf("HTTP/1.1 %s\r\n", status);
  client.printf("Content-Type: %s\r\n", contentType);
  client.println("Connection: close");
  client.println("Cache-Control: no-store");
  if (extraHeaders != nullptr) {
    client.print(extraHeaders);
  }
  client.println();
}

void sendIndexPage(WiFiClient &client) {
  sendHttpHeader(client, "200 OK", "text/html; charset=utf-8");
  client.println("<!doctype html><html><head><meta name='viewport' content='width=device-width,initial-scale=1'>");
  client.println("<title>AI Goggles Live Preview</title>");
  client.println("<style>body{font-family:-apple-system,BlinkMacSystemFont,sans-serif;margin:20px;background:#111;color:#eee}img{max-width:100%;border:1px solid #555}button{font-size:16px;margin:4px;padding:8px 12px}</style>");
  client.println("</head><body><h1>AI Goggles Live Preview</h1>");
  client.println("<img src='/stream' alt='live preview'>");
  client.println("<p>Live preview is MJPEG. Local recording is saved to microSD.</p>");
  client.println("<p><a href='/status'>Status JSON</a> · <a href='/capture'>Capture JPEG</a></p>");
  client.println("<script>setInterval(()=>fetch('/status').then(r=>r.json()).then(s=>document.title=(s.recording?'REC ':'')+'AI Goggles Live Preview').catch(()=>{}),2000)</script>");
  client.println("</body></html>");
}

void sendStatusJson(WiFiClient &client) {
  sendHttpHeader(client, "200 OK", "application/json");
  RecordingSummary &summary = recordingSession.summary;
  client.println("{");
  client.printf("  \"recording\": %s,\n", isRecordingActive() ? "true" : "false");
  client.printf("  \"recording_state\": \"%s\",\n", recordingStateName(recordingSession.state));
  client.printf("  \"storage_mode\": \"%s\",\n", isRecordingActive() ? storageModeName(summary.storageMode) : "none");
  client.printf("  \"clip\": \"%s\",\n", isRecordingActive() ? summary.outputPath : "");
  client.printf("  \"target_fps\": %u,\n", isRecordingActive() ? summary.targetFps : PREVIEW_TARGET_FPS);
  client.printf("  \"actual_fps\": %.2f,\n", currentSessionFps());
  client.printf("  \"successful_frames\": %lu,\n", static_cast<unsigned long>(summary.successfulFrames));
  client.printf("  \"failed_frames\": %lu,\n", static_cast<unsigned long>(summary.failedFrames));
  client.printf("  \"preview_clients\": %u,\n", hasPreviewClient() ? 1 : 0);
  client.printf("  \"preview_frames_sent\": %lu,\n", static_cast<unsigned long>(previewFramesSent));
  client.printf("  \"preview_dropped_frames\": %lu,\n", static_cast<unsigned long>(previewFramesDropped));
  client.printf("  \"preview_disconnects\": %lu,\n", static_cast<unsigned long>(previewDisconnects));
  client.printf("  \"free_heap\": %lu,\n", static_cast<unsigned long>(ESP.getFreeHeap()));
  client.printf("  \"free_psram\": %lu,\n", static_cast<unsigned long>(ESP.getFreePsram()));
  client.printf("  \"sd_ready\": %s,\n", sdInitialized ? "true" : "false");
  client.printf("  \"wifi_connected\": %s,\n", wifiConnected ? "true" : "false");
  client.printf("  \"ip\": \"%s\"\n", wifiConnected ? WiFi.localIP().toString().c_str() : "");
  client.println("}");
}

void sendBusy(WiFiClient &client, const char *message) {
  sendHttpHeader(client, "409 Conflict", "text/plain; charset=utf-8");
  client.println(message);
}

void sendCaptureJpeg(WiFiClient &client) {
  if (isRecordingActive() || hasPreviewClient()) {
    sendBusy(client, "Camera pipeline is busy. Use /stream during preview or stop recording first.");
    return;
  }

  if (!ensureCameraForProfile(PROFILES[RECOMMENDED_PROFILE_INDEX])) {
    sendHttpHeader(client, "500 Internal Server Error", "text/plain; charset=utf-8");
    client.println("Camera unavailable");
    return;
  }

  camera_fb_t *frame = esp_camera_fb_get();
  if (frame == nullptr || frame->format != PIXFORMAT_JPEG) {
    if (frame != nullptr) {
      esp_camera_fb_return(frame);
    }
    sendHttpHeader(client, "500 Internal Server Error", "text/plain; charset=utf-8");
    client.println("Capture failed");
    return;
  }

  client.println("HTTP/1.1 200 OK");
  client.println("Content-Type: image/jpeg");
  client.printf("Content-Length: %u\r\n", static_cast<unsigned int>(frame->len));
  client.println("Cache-Control: no-store");
  client.println("Connection: close");
  client.println();
  client.write(frame->buf, frame->len);
  esp_camera_fb_return(frame);
}

void startStreamResponse(WiFiClient &client) {
  if (!previewServerEnabled) {
    sendBusy(client, "Preview server is disabled. Send v over Serial/BLE to enable it.");
    return;
  }

  if (hasPreviewClient()) {
    sendBusy(client, "Only one /stream client is supported in this V0 firmware.");
    return;
  }

  client.setNoDelay(true);
  client.setTimeout(1);
  client.println("HTTP/1.1 200 OK");
  client.println("Content-Type: multipart/x-mixed-replace; boundary=frame");
  client.println("Cache-Control: no-store");
  client.println("Connection: keep-alive");
  client.println();
  previewClient = client;
  Serial.println("Preview stream client connected.");
}

void updateHttpServer() {
  ensureWiFiConnection();
  if (!wifiConnected || !httpServerStarted) {
    return;
  }

  if (previewClient && !previewClient.connected()) {
    closePreviewClient("client closed");
  }

  WiFiClient client = httpServer.available();
  if (!client) {
    return;
  }

  String requestLine = readHttpRequestLine(client);
  if (requestLine.length() == 0) {
    client.stop();
    return;
  }
  drainHttpHeaders(client);

  int firstSpace = requestLine.indexOf(' ');
  int secondSpace = requestLine.indexOf(' ', firstSpace + 1);
  String method = firstSpace > 0 ? requestLine.substring(0, firstSpace) : "";
  String path = secondSpace > firstSpace ? requestLine.substring(firstSpace + 1, secondSpace) : "/";
  int queryIndex = path.indexOf('?');
  if (queryIndex >= 0) {
    path = path.substring(0, queryIndex);
  }

  if (method != "GET") {
    sendHttpHeader(client, "405 Method Not Allowed", "text/plain; charset=utf-8");
    client.println("Only GET is supported");
    client.stop();
    return;
  }

  if (path == "/") {
    sendIndexPage(client);
    client.stop();
  } else if (path == "/status") {
    sendStatusJson(client);
    client.stop();
  } else if (path == "/capture") {
    sendCaptureJpeg(client);
    client.stop();
  } else if (path == "/stream") {
    startStreamResponse(client);
  } else {
    sendHttpHeader(client, "404 Not Found", "text/plain; charset=utf-8");
    client.println("Not found");
    client.stop();
  }
}

// ============================================================
// Controls
// ============================================================

void printHelp() {
  Serial.println();
  Serial.println("Commands:");
  Serial.println("  p - take one photo");
  Serial.println("  r - start SD MJPEG recording with Wi-Fi preview available");
  Serial.println("  x - stop current SD recording and write metadata");
  Serial.println("  j - start JPEG sequence debug recording");
  Serial.println("  m - start SD MJPEG recording");
  Serial.println("  v - enable/disable Wi-Fi preview server");
  Serial.println("  w - print Wi-Fi status, IP, and preview URLs");
  Serial.println("  s - print next file indexes");
  Serial.println("  i - print hardware, memory, SD, and profile info");
  Serial.println("  b - run video smoothness benchmark suite");
  Serial.println("  h - print this help");
  Serial.println();
  Serial.println("BLE:");
  Serial.printf("  Device: %s\n", BLE_DEVICE_NAME);
  Serial.printf("  Service: %s\n", BLE_SERVICE_UUID);
  Serial.printf("  Control characteristic: %s\n", BLE_CONTROL_UUID);
  Serial.println("  Write p, r, x, j, m, v, w, s, i, b, or h as text/UTF-8.");
}

void executeCommand(char command, const char *source) {
  if (command >= 'A' && command <= 'Z') {
    command = static_cast<char>(command - 'A' + 'a');
  }

  Serial.printf("%s command: %c\n", source, command);

  if (command == 'p') {
    if (isRecordingActive()) {
      Serial.println("Photo command ignored while recording. Send x first.");
      setBleStatus("error: recording");
      return;
    }
    setBleStatus("busy: taking photo");
    takeSinglePhoto();
    setBleStatus("ready: photo done");
  } else if (command == 'r') {
    startRecordingSession(PROFILES[RECOMMENDED_PROFILE_INDEX], "recommended");
  } else if (command == 'x') {
    requestStopRecordingSession(source);
  } else if (command == 'j') {
    startRecordingSession(PROFILES[JPEG_SEQUENCE_PROFILE_INDEX], "jpeg debug");
  } else if (command == 'm') {
    startRecordingSession(PROFILES[RECOMMENDED_PROFILE_INDEX], "mjpeg");
  } else if (command == 'v') {
    previewServerEnabled = !previewServerEnabled;
    if (!previewServerEnabled && hasPreviewClient()) {
      closePreviewClient("preview disabled");
    }
    Serial.printf("Preview server %s.\n", previewServerEnabled ? "enabled" : "disabled");
    setBleStatus(previewServerEnabled ? "ready: preview enabled" : "ready: preview disabled");
  } else if (command == 'w') {
    printWiFiStatus();
    setBleStatus(wifiConnected ? WiFi.localIP().toString() : "wifi not connected");
  } else if (command == 's') {
    String status =
      "photo=" + String(nextPhotoIndex) +
      ", clip=" + String(nextClipIndex) +
      ", rec=" + String(recordingStateName(recordingSession.state)) +
      ", wifi=" + String(wifiConnected ? WiFi.localIP().toString() : "off");
    Serial.printf("Next photo index: %lu\n", static_cast<unsigned long>(nextPhotoIndex));
    Serial.printf("Next clip index: %lu\n", static_cast<unsigned long>(nextClipIndex));
    Serial.printf("Recording state: %s\n", recordingStateName(recordingSession.state));
    setBleStatus(status);
  } else if (command == 'i') {
    printSystemInfo();
    setBleStatus("ready: info printed");
  } else if (command == 'b') {
    if (isRecordingActive()) {
      Serial.println("Benchmark ignored while recording. Send x first.");
      setBleStatus("error: recording");
      return;
    }
    if (hasPreviewClient()) {
      closePreviewClient("benchmark starting");
    }
    runBenchmarkSuite();
  } else if (command == 'h' || command == '?') {
    printHelp();
    setBleStatus("ready: write p,r,x,j,m,v,w,s,i,b,h");
  } else if (command == '\n' || command == '\r') {
    return;
  } else {
    Serial.printf("Unknown command: %c\n", command);
    setBleStatus("error: write p,r,x,j,m,v,w,s,i,b,h");
  }
}

void updateSerialCommands() {
  while (Serial.available() > 0) {
    char command = static_cast<char>(Serial.read());
    executeCommand(command, "Serial");
  }
}

void updateBleCommands() {
  if (!hasPendingBleCommand) {
    return;
  }

  char command = pendingBleCommand;
  pendingBleCommand = '\0';
  hasPendingBleCommand = false;
  executeCommand(command, "BLE");
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
        if (isRecordingActive()) {
          requestStopRecordingSession("button short press");
        } else {
          takeSinglePhoto();
        }
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
    if (isRecordingActive()) {
      requestStopRecordingSession("button long press");
    } else {
      startRecordingSession(PROFILES[RECOMMENDED_PROFILE_INDEX], "button");
    }
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
  Serial.println("AI_Goggles V0 Camera Prototype");
  Serial.println("XIAO ESP32S3 Sense");
  Serial.println("========================================");

  if (psramFound()) {
    frameTimings = static_cast<FrameTiming *>(ps_malloc(sizeof(FrameTiming) * MAX_TIMING_FRAMES));
  }

  if (frameTimings == nullptr) {
    static FrameTiming fallbackTimings[240];
    frameTimings = fallbackTimings;
    frameTimingCapacity = 240;
    Serial.println("WARNING: PSRAM timing buffer allocation failed; timing CSV capacity is reduced.");
  } else {
    frameTimingCapacity = MAX_TIMING_FRAMES;
  }

  Serial.printf("Timing rows capacity: %lu\n", static_cast<unsigned long>(frameTimingCapacity));

  Serial.println("Initializing camera...");
  if (!initializeCameraForProfile(PROFILES[RECOMMENDED_PROFILE_INDEX])) {
    Serial.println("FATAL ERROR: Camera could not start.");
    fatalBlink(1, 100, 900);
  }

  Serial.println("Initializing microSD card...");
  if (!mountMicroSD(SD_SAFE_FREQUENCY)) {
    Serial.println("WARNING: microSD could not start. Preview can still run, but SD recording commands will fail until SD is available.");
  } else {
    findNextAvailableIndexes();
  }

  Serial.println("Initializing BLE control...");
  initializeBLE();

  Serial.println("Initializing Wi-Fi preview server...");
  initializeWiFiAndHttp();

  stableButtonState = digitalRead(BUTTON_PIN);
  lastRawButtonState = stableButtonState;
  lastButtonChangeMs = millis();

  Serial.println();
  Serial.println("System ready.");
  printHelp();
  blinkRecordingLed(3, 150, 150);
}

void loop() {
  updateSerialCommands();
  updateBleCommands();
  updateButton();
  updateHttpServer();
  updateRecordingSession();
  updatePreviewOnlyCapture();
  delay(2);
}
