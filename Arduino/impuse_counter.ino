#define REQUIRESNEW 1
#include <DallasTemperature.h>
// #include <SPI.h>
// #include <LedControl.h>

#define IMP_PIN 2
#define LED_PIN 13
#define FAN_FINS 7
#define INTERRUPTS_TO_RPM(impulses,seconds) ((60.0/float(seconds)) * (float(impulses)/float(FAN_FINS)))

#define TEMP_SENSOR_BUS 7

volatile unsigned long imp_counter;

OneWire oneWireBus(TEMP_SENSOR_BUS);
DallasTemperature temp_sensor(&oneWireBus);
DeviceAddress temp_sensor_address;

byte led_state = HIGH;

/*
LedControl lcd=LedControl(12,11,10,2);

void lcdFloat (double display_value) {
  unsigned long val = abs(display_value) * 100;

  int i = 0;
  while ((val > 0 or i < 3) and i < 8) {
    lcd.setDigit(0, i, val % 10, (i == 2));
    val = long(val / 10);
    i ++;
  }
  // sign
  if (display_value < 0 and i < 8) {
    lcd.setChar(0, i, '-', false);
  }
}

void lcdTwoInts(int val1, int val2) {
  int i = 0;
  
  if (val1 == 0) {
    lcd.setDigit(0, 0, 0, false);
  } else {
    while (i < 4 and val1 != 0) {
      lcd.setDigit(0, i, val1 % 10, false);
      i ++;
      val1 = val1 / 10;
    }
  }
  
  i = 4;
  if (val2 == 0) {
    lcd.setDigit(0, 4, 0, false);
  } else {
    while (i < 8 and val2 != 0) {
      lcd.setDigit(0, i, val2 % 10, false);
      i ++;
      val2 = val2 / 10;
    }
  }
}*/

void count_imp () {
  imp_counter ++;
}

void setup() {
  Serial.begin(9600);
  pinMode (IMP_PIN, INPUT);
  pinMode (LED_PIN, OUTPUT);

//  lcd.shutdown(0, false);
//  lcd.setIntensity(0,1);
//
//  lcd.clearDisplay(0);
  
  temp_sensor.begin();
  temp_sensor.getAddress(temp_sensor_address, 0);
  temp_sensor.setResolution(temp_sensor_address, 12);

  imp_counter = 0;
  attachInterrupt(digitalPinToInterrupt(IMP_PIN), count_imp, FALLING);
}

void loop() {
  led_state = 1-led_state;
  digitalWrite(LED_PIN, led_state);
  // reset impulse counter and mark time
  imp_counter = 0;
  unsigned long t_start = millis();

  // request the temperatures and wait a little time
  temp_sensor.requestTemperatures();
  float temperature = temp_sensor.getTempCByIndex(0);
  
  unsigned long t_end = t_start + 1000;
  while (millis() < t_end) {
    delay(10);
  }
  
  // fetch impulse counter and mark time
  unsigned long counted = imp_counter;
  t_end = millis();
  
  float rpm = INTERRUPTS_TO_RPM(counted, float(t_end - t_start) / 1000.0);
  
//  Serial.print ("RPM: "); Serial.print (rpm); 
//  Serial.print (" IMP: "); Serial.print(counted);
//  Serial.print (" DT:  "); Serial.print(float(t_end - t_start));
//  Serial.print (" TMP "); Serial.println(temperature);
  Serial.print ("S");
  Serial.print (rpm); 
  Serial.print (","); 
//  Serial.print (counted); 
//  Serial.print (","); 
  Serial.print(temperature);
  Serial.println("E");

  // lcd.clearDisplay(0);
  // lcdTwoInts(round(temperature), round(rpm));
  // lcdFloat (rpm);
}

//void loop() {
//  // reset impulse counter and mark time
//  imp_counter = 0;
//  
//  delay(1000);
//  
//  unsigned long counted = imp_counter;
//  
//  float rpm = INTERRUPTS_TO_RPM(counted, 1.0);
//  
//  Serial.print("RPM: "); Serial.print (rpm); 
//  Serial.print("Cnt: "); Serial.print (counted); 
//  Serial.println();
//}
