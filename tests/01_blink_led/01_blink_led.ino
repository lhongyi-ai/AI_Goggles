constexpr int RECORD_LED_PIN = D2;

void setup() {
  pinMode(RECORD_LED_PIN, OUTPUT);
}

void loop() {
  digitalWrite(RECORD_LED_PIN, HIGH);
  delay(500);
  digitalWrite(RECORD_LED_PIN, LOW);
  delay(500);
}
