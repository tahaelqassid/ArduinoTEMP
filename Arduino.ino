#include <DHT.h>
#include <LiquidCrystal_I2C.h>

#define DHTPIN    2
#define DHTTYPE   DHT11
#define GREENLED  6
#define YELLOWLED 7
#define REDLED    8
#define BUZZER    9

#define TEMP_NORMAL 30.0
#define TEMP_WARM   31.0

DHT dht(DHTPIN, DHTTYPE);
LiquidCrystal_I2C lcd(0x27, 16, 2);

void allLedsOff() {
  digitalWrite(GREENLED,  LOW);
  digitalWrite(YELLOWLED, LOW);
  digitalWrite(REDLED,    LOW);
  noTone(BUZZER);
  digitalWrite(BUZZER, LOW);
}

void setup() {
  Serial.begin(9600);
  dht.begin();

  pinMode(GREENLED,  OUTPUT);
  pinMode(YELLOWLED, OUTPUT);
  pinMode(REDLED,    OUTPUT);
  pinMode(BUZZER,    OUTPUT);

  allLedsOff();

  lcd.init();
  lcd.backlight();

  lcd.setCursor(0, 0);
  lcd.print("  Temp  Alarm   ");
  lcd.setCursor(0, 1);
  lcd.print("   Starting...  ");
  delay(2000);
  lcd.clear();
}

void loop() {
  float temp = dht.readTemperature();
  float hum  = dht.readHumidity();

  if (isnan(temp) || isnan(hum)) {
    allLedsOff();
    lcd.setCursor(0, 0);
    lcd.print("Sensor Error!   ");
    lcd.setCursor(0, 1);
    lcd.print("Check DHT11 !!  ");
    Serial.println("ERROR: DHT11 read failed");
    delay(2000);
    return;
  }

  lcd.setCursor(0, 0);
  lcd.print("Temp: ");
  lcd.print(temp, 1);
  lcd.print((char)223);
  lcd.print("C   ");

  lcd.setCursor(8, 0);
  lcd.print("H:");
  lcd.print(hum, 0);
  lcd.print("%  ");

  Serial.print("Temp: "); Serial.print(temp);
  Serial.print("C  |  Hum: "); Serial.print(hum);
  Serial.println("%");

  if (temp < TEMP_NORMAL) {
    allLedsOff();
    digitalWrite(BUZZER, LOW);
    lcd.setCursor(0, 1);
    lcd.print("Status: NORMAL  ");
    Serial.println("Status: NORMAL");

    digitalWrite(GREENLED, HIGH);
    delay(900);
    digitalWrite(GREENLED, LOW);
    delay(100);
  }

  else if (temp >= TEMP_NORMAL && temp < TEMP_WARM) {
    allLedsOff();
    digitalWrite(BUZZER, LOW);
    lcd.setCursor(0, 1);
    lcd.print("Status: WARM    ");
    Serial.println("Status: WARM");

    digitalWrite(YELLOWLED, HIGH);
    delay(400);
    digitalWrite(YELLOWLED, LOW);
    delay(100);
  }

  else {
    allLedsOff();
    lcd.setCursor(0, 1);
    lcd.print("!! HIGH ALERT !!");
    Serial.println("Status: HIGH ALERT !!!");

    for (int i = 0; i < 3; i++) {
      digitalWrite(REDLED, HIGH);
      digitalWrite(BUZZER, HIGH);
      delay(200);
      digitalWrite(REDLED, LOW);
      digitalWrite(BUZZER, LOW);
      delay(200);
    }
  }
}