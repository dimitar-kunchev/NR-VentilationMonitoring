# NR-VentilationMonitoring
Raspberry+Arduino system to gather information from multiple sensors on single serial port and save them in MySQL 
database

This project was built to monitor the ventilation system in an industrial setting. Intention is to have 6 sensor boards, 
each acting as a sensor, providing airflow readings (anemometer) and temperature. Data is collected by a Raspberry Pi 
and saved in a database (MySQL).

This code is not intended to be used as-is. Instead I wanted to show how one could overcome the limitation of having 
a single serial port on an Raspberry using a multiplexor IC (in my case CD74HC4051E). This chip acts as sort of a 
sophisticated relay. With 3 address pins you connect one common pin to 8 slave ones. This way you can connect the serial 
port to each of the sensors but you can talk to only one at a time. For that reason the sensors just send data 
continuously every 1 second and the central hub (the raspberry) just loops trough all of them and waits for information. 
If needed one could utilize a version of that IC with 2 common pins and 4 slaves having both RX and TX or two ICs - 
one for RX and one for TX lines. But since I m just reading from the sensors I connected only one IC with the RX line.

The sensors are implemented as Pololu A-Star 328pb boards and programmed with Arduino. Temperature data is read via
DS18B20 sensors and airflow is implemented with a propeller (from 50mm PC fan), IR phototransistor and IR LED, 
counting the number of times the blades pass between the sensor and the LED. This design is suitable for very DIY 
project and provides good temperature readings. As for airflow rates - it depends on how well the blades spin. If 
friction is very low you can get as low as 1m/s and up to 20m/s reliable readings. If accuracy is needed this is not
a recommended approach really.

### Configuration
Add a config.ini file, following the details in the config.ini.sample. Should be self-explanatory

### Database
Use the db.sql as reference.

### Cron jobs
There is an extra aggregate.py file that will periodically aggregate (average) the readings from the sensors into 
larger and larger chunks. Use the sensors-aggregation-cron.sample as reference, adjust the paths as needed

### Service
main.py is the main file that does the reading of the data. It is intended to be run as service. Place 
ventilation-monitoring.service in /etc/systemd/system and using the systemctl commands enable and start the service.

Make sure yuo check the paths to where you have placed the executable files.

### Calibration
The temperature sensor comes factory-calibrated but the implementation of the anemometer requires we convert from
RPM readings (sent by the sensors) to whatever unit we like (in my case - m<sup>3</sup>/h). This is done with a simple
multiplier. Each sensor may have a different value - these are defined in the config.ini file. This is dimensionless
really so what multiplier you use and how you refer to the reading is up to you. Generally anemometers read speed
(e.g. meters/second or miles/hour) but in my case it was easier to just multiply it to get cubic meters.

### Wiring
Diagram is published on EasyEda.
https://easyeda.com/dimitar.kunchev/Pi-Arduino-Ventilation-Monitoring

### License
Feel free to share and modify the code. Use at your own risk and don't blame me if it doesn't work or something blows 
up. If you need help or like the idea - drop me an email. See the license.txt file for legal details.