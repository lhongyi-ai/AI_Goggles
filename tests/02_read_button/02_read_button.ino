constexpr int BUTTON_PIN = D1;

int previousState = HIGH;

void setup() {
  pinMode(BUTTON_PIN, INPUT_PULLUP);
  Serial.begin(115200);

  unsigned long startMs = millis();
  while (!Serial && millis() - startMs < 5000) {
    delay(10);
  }

  Serial.println("Button test ready.");
  Serial.println("Released = HIGH, pressed = LOW.");
}

void loop() {
  int state = digitalRead(BUTTON_PIN);

  if (state != previousState) {
    previousState = state;
    Serial.println(state == LOW ? "Button pressed" : "Button released");
  }

  delay(20);
}
