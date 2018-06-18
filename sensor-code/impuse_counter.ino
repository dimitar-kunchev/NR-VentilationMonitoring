/**
 * Sensor readings and passing to the hub
 * https://github.com/dimitar-kunchev/NR-VentilationMonitoring
 * @author: Dimitar Kunchev
 * @license: See the LICENSE file
 * @email: dimitar.kunchev@racecloud.net
 */
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

void count_imp () {
  imp_counter ++;
}

void setup() {
  Serial.begin(9600);
  pinMode (IMP_PIN, INPUT);
  pinMode (LED_PIN, OUTPUT);

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
  
  Serial.print ("S");
  Serial.print (rpm); 
  Serial.print (","); 
  Serial.print(temperature);
  Serial.println("E");

}

