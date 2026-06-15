#include <Arduino.h>
#include "FS.h"
#include "SD.h"
#include "SPI.h"

constexpr int SD_CS_PIN = 21;
constexpr int SD_SCK_PIN = D8;
constexpr int SD_MISO_PIN = D9;
constexpr int SD_MOSI_PIN = D10;

void setup() {
  Serial.begin(115200);

  unsigned long startMs = millis();
  while (!Serial && millis() - startMs < 5000) {
    delay(10);
  }

  Serial.println("microSD write test starting.");

  SPI.begin(SD_SCK_PIN, SD_MISO_PIN, SD_MOSI_PIN, SD_CS_PIN);

  if (!SD.begin(SD_CS_PIN, SPI, 10000000)) {
    Serial.println("SD mount failed");
    return;
  }

  if (SD.cardType() == CARD_NONE) {
    Serial.println("No SD card detected");
    return;
  }

  Serial.println("SD card mounted");

  File file = SD.open("/test.txt", FILE_WRITE);
  if (!file) {
    Serial.println("Failed to open /test.txt");
    return;
  }

  file.println("V0 test");
  file.close();

  Serial.println("File written successfully: /test.txt");
}

void loop() {
}
