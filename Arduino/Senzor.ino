#define analogPin A0 // аналоговый выход MQ2 подключен к пину A0 Arduino

float analogValue; // для аналогового значения
byte digitalValue; // для цифрового значения, можно, кстати и boolean, но не суть
int ledRed = 6;
int ledGreen = 4;

void setup() {
  Serial.begin(9600); // инициализация последовательного порта
  pinMode(analogPin, INPUT); // режим работы аналогового пина
  pinMode(ledRed, OUTPUT);
  pinMode(ledGreen, OUTPUT);
  delay(1000); // устаканимся
}

void loop() {
  analogValue = analogRead(analogPin); // чтение аналогового значения

  if (analogValue >= 220) { // от 80 до 415 мг значение со2
    digitalWrite (ledRed, HIGH);
    digitalWrite (ledGreen, LOW);
    delay(500);
  } else {
      digitalWrite(ledRed, LOW);
      digitalWrite (ledGreen, HIGH);
      delay(500);
  }
 
  Serial.println(analogValue);

  delay(1000); // задержка, чтобы не мельтешило перед глазами
}
