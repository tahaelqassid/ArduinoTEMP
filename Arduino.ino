#include <DHT.h>
#include <LiquidCrystal.h>

#define DHTPIN 7     
#define DHTTYPE DHT11   // DHT11 sensor
DHT dht(DHTPIN, DHTTYPE);

LiquidCrystal lcd(12, 11, 5, 4, 3, 2);

#define LED1_PIN 8
#define LED2_PIN 9
#define LED3_PIN 10
#define LED4_PIN 13
#define ACTIVE_BUZZER_PIN 6
#define PASSIVE_BUZZER_PIN A0

void setup() {
  lcd.begin(16, 2);
  dht.begin();

  pinMode(LED1_PIN, OUTPUT);
  pinMode(LED2_PIN, OUTPUT);
  pinMode(LED3_PIN, OUTPUT);
  pinMode(LED4_PIN, OUTPUT);
  pinMode(ACTIVE_BUZZER_PIN, OUTPUT);
  pinMode(PASSIVE_BUZZER_PIN, OUTPUT);

  Serial.begin(9600);
}

void loop() {
  float h = dht.readHumidity();
  float t = dht.readTemperature();

  if (isnan(h) || isnan(t)) {
    lcd.setCursor(0, 0);
    lcd.print("Error Reading ");
    return;
  }

  lcd.setCursor(0, 0);
  lcd.print("Temp: ");
  lcd.print(t);
  lcd.print("C");

  lcd.setCursor(0, 1);
  lcd.print("Humidity: ");
  lcd.print(h);
  lcd.print("%");

  if (t < 25) {
    digitalWrite(LED1_PIN, HIGH);  // Room temp
    digitalWrite(LED2_PIN, LOW);
    digitalWrite(LED3_PIN, LOW);
    digitalWrite(LED4_PIN, LOW);
    digitalWrite(ACTIVE_BUZZER_PIN, LOW);
  } else if (t >= 25 && t < 30) {
    digitalWrite(LED1_PIN, LOW);
    digitalWrite(LED2_PIN, HIGH);  // Warm
    digitalWrite(LED3_PIN, LOW);
    digitalWrite(LED4_PIN, LOW);
    digitalWrite(ACTIVE_BUZZER_PIN, LOW);
  } else if (t >= 30 && t < 35) {
    digitalWrite(LED1_PIN, LOW);
    digitalWrite(LED2_PIN, LOW);
    digitalWrite(LED3_PIN, HIGH);  // Hot
    digitalWrite(LED4_PIN, LOW);
    digitalWrite(ACTIVE_BUZZER_PIN, HIGH); //active buzzer
  } else {
    digitalWrite(LED1_PIN, LOW);
    digitalWrite(LED2_PIN, LOW);
    digitalWrite(LED3_PIN, LOW);
    digitalWrite(LED4_PIN, HIGH);  // Very hot
    digitalWrite(ACTIVE_BUZZER_PIN, HIGH);
    tone(PASSIVE_BUZZER_PIN, 1000); // active + passive
  }

  delay(2000);
}
