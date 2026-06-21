/*
  AI_Goggles V0 camera prototype
  Board: Seeed Studio XIAO ESP32S3 Sense

  Controls:
  - p: take one JPEG photo
  - r: record one clip with the recommended profile
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
#include <math.h>
#include <stdlib.h>
#include "esp_camera.h"
#include "esp_timer.h"
#include "FS.h"
#include "SD.h"
#include "SPI.h"

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
constexpr size_t RECOMMENDED_PROFILE_INDEX = 0;

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
  uint32_t totalFrameDurationUs;
  uint32_t frameIntervalUs;
  uint32_t jpegSizeBytes;
  bool writeSuccess;
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
  uint64_t captureStartUs = 0;
  uint64_t frameReadyUs = 0;
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

// ============================================================
// Forward declarations
// ============================================================

void setBleStatus(const String &status);
void queueBleCommand(char command);
void executeCommand(char command, const char *source);
bool recordClip(const RecordingProfile &profile, const char *reason, RecordingSummary *summaryOut);

class GogglesServerCallbacks : public BLEServerCallbacks {
  void onConnect(BLEServer *server) override {
    (void)server;
    bleClientConnected = true;
    Serial.println("BLE client connected.");
    setBleStatus("connected: write p,r,s,i,b,h");
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

const char *grabModeName(camera_grab_mode_t mode) {
  return mode == CAMERA_GRAB_LATEST ? "latest" : "when_empty";
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

  if (command != 'p' && command != 'r' && command != 's' && command != 'h' && command != 'i' && command != 'b') {
    setBleStatus("error: write p,r,s,i,b,h");
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
  setBleStatus("ready: write p,r,s,i,b,h");

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

CaptureWriteResult captureAndWriteFrame(const char *filePath, File *mjpegFile) {
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
  size_t bytesWritten = targetFile.write(frame->buf, frame->len);
  result.sdWriteDurationUs = static_cast<uint32_t>(nowUs() - writeStartUs);

  uint64_t closeStartUs = nowUs();
  if (mjpegFile == nullptr) {
    imageFile.close();
  }
  result.sdCloseDurationUs = static_cast<uint32_t>(nowUs() - closeStartUs);

  size_t expectedBytes = frame->len;
  esp_camera_fb_return(frame);

  if (bytesWritten == expectedBytes) {
    result.success = true;
  } else if (mjpegFile == nullptr && filePath != nullptr) {
    SD.remove(filePath);
  }

  return result;
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

  file.println("capture_attempt,saved_frame_index,scheduled_start_us,capture_start_us,frame_ready_us,capture_duration_us,sd_open_duration_us,sd_write_duration_us,sd_close_duration_us,total_frame_duration_us,frame_interval_us,jpeg_size_bytes,write_success,deadline_missed");

  for (uint32_t i = 0; i < summary.timingRowsStored; ++i) {
    const FrameTiming &row = frameTimings[i];
    file.printf("%lu,%lu,%llu,%llu,%llu,%lu,%lu,%lu,%lu,%lu,%lu,%lu,%u,%u\n",
                static_cast<unsigned long>(row.captureAttempt),
                static_cast<unsigned long>(row.savedFrameIndex),
                row.scheduledStartUs,
                row.captureStartUs,
                row.frameReadyUs,
                static_cast<unsigned long>(row.captureDurationUs),
                static_cast<unsigned long>(row.sdOpenDurationUs),
                static_cast<unsigned long>(row.sdWriteDurationUs),
                static_cast<unsigned long>(row.sdCloseDurationUs),
                static_cast<unsigned long>(row.totalFrameDurationUs),
                static_cast<unsigned long>(row.frameIntervalUs),
                static_cast<unsigned long>(row.jpegSizeBytes),
                row.writeSuccess ? 1 : 0,
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
      row.totalFrameDurationUs = result.captureStartUs > 0 ? static_cast<uint32_t>(frameEndUs - result.captureStartUs) : 0;
      row.frameIntervalUs = previousCaptureStartUs > 0 && result.captureStartUs > previousCaptureStartUs
        ? static_cast<uint32_t>(result.captureStartUs - previousCaptureStartUs)
        : 0;
      row.jpegSizeBytes = result.jpegSizeBytes;
      row.writeSuccess = result.success;
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
// Controls
// ============================================================

void printHelp() {
  Serial.println();
  Serial.println("Commands:");
  Serial.println("  p - take one photo");
  Serial.println("  r - record one clip with the recommended profile");
  Serial.println("  s - print next file indexes");
  Serial.println("  i - print hardware, memory, SD, and profile info");
  Serial.println("  b - run video smoothness benchmark suite");
  Serial.println("  h - print this help");
  Serial.println();
  Serial.println("BLE:");
  Serial.printf("  Device: %s\n", BLE_DEVICE_NAME);
  Serial.printf("  Service: %s\n", BLE_SERVICE_UUID);
  Serial.printf("  Control characteristic: %s\n", BLE_CONTROL_UUID);
  Serial.println("  Write p, r, s, i, b, or h as text/UTF-8.");
}

void executeCommand(char command, const char *source) {
  if (command >= 'A' && command <= 'Z') {
    command = static_cast<char>(command - 'A' + 'a');
  }

  Serial.printf("%s command: %c\n", source, command);

  if (command == 'p') {
    setBleStatus("busy: taking photo");
    takeSinglePhoto();
    setBleStatus("ready: photo done");
  } else if (command == 'r') {
    setBleStatus("busy: recording");
    RecordingSummary summary;
    recordClip(PROFILES[RECOMMENDED_PROFILE_INDEX], "recommended", &summary);
    setBleStatus("ready: recording done");
  } else if (command == 's') {
    String status =
      "photo=" + String(nextPhotoIndex) +
      ", clip=" + String(nextClipIndex) +
      ", ble=" + String(bleClientConnected ? "connected" : "advertising");
    Serial.printf("Next photo index: %lu\n", static_cast<unsigned long>(nextPhotoIndex));
    Serial.printf("Next clip index: %lu\n", static_cast<unsigned long>(nextClipIndex));
    setBleStatus(status);
  } else if (command == 'i') {
    printSystemInfo();
    setBleStatus("ready: info printed");
  } else if (command == 'b') {
    runBenchmarkSuite();
  } else if (command == 'h' || command == '?') {
    printHelp();
    setBleStatus("ready: write p,r,s,i,b,h");
  } else if (command == '\n' || command == '\r') {
    return;
  } else {
    Serial.printf("Unknown command: %c\n", command);
    setBleStatus("error: write p,r,s,i,b,h");
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
    RecordingSummary summary;
    recordClip(PROFILES[RECOMMENDED_PROFILE_INDEX], "button", &summary);
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
    Serial.println("FATAL ERROR: microSD could not start.");
    fatalBlink(2, 150, 350);
  }

  findNextAvailableIndexes();

  Serial.println("Initializing BLE control...");
  initializeBLE();

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
  delay(2);
}
