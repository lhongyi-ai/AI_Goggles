constexpr int BUTTON_PIN = D1;
constexpr int RECORD_LED_PIN = D2;

void setup() {
  pinMode(BUTTON_PIN, INPUT_PULLUP);
  pinMode(RECORD_LED_PIN, OUTPUT);
  digitalWrite(RECORD_LED_PIN, LOW);
}

void loop() {
  bool pressed = digitalRead(BUTTON_PIN) == LOW;
  digitalWrite(RECORD_LED_PIN, pressed ? HIGH : LOW);
  delay(10);
}
