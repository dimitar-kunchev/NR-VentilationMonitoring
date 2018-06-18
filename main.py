#!/usr/bin/python3
"""
Sensors aggregation and storage.
https://github.com/dimitar-kunchev/NR-VentilationMonitoring
@author: Dimitar Kunchev
@license: See the LICENSE file
@email: dimitar.kunchev@racecloud.net
"""
import RPi.GPIO as GPIO
import serial
import time
import pymysql
import configparser
import json
import os
import sys
import threading
import queue

db_connection = None  # type: pymysql.Connection

# These declarations use some default settings. Adjust with the config file
PIN_S0 = 4
PIN_S1 = 3
PIN_S2 = 17
PIN_EN = 18

SENSORS_COUNT = 6

# Conversion of RPM to airflow for each sensor
RPM_TO_AIRFLOW_COEFFICIENTS = [
    120.0 / 6000.0,
    120.0 / 6000.0,
    120.0 / 6000.0,
    120.0 / 6000.0,
    120.0 / 6000.0,
    120.0 / 6000.0
]

# When set to True the mysql thread should stop
STOP_MYSQL_THREAD_FLAG = False


def set_slave_address(addr: int):
    """Sets the S* pins high/low to conenct to a sensor. Note we use inverted logic. Depends on your wiring!"""
    GPIO.output(PIN_S0, GPIO.LOW if (0x01 & addr) else GPIO.HIGH)
    GPIO.output(PIN_S1, GPIO.LOW if (0x01 & (addr >> 1)) else GPIO.HIGH)
    GPIO.output(PIN_S2, GPIO.LOW if (0x01 & (addr >> 2)) else GPIO.HIGH)


def mysql_thread_func(config: configparser.ConfigParser, q: queue.Queue):
    """The MySQL thread. Push queries in the queue and it executes them. Two while loops so we reconnect when
     something goes wrong"""
    while not STOP_MYSQL_THREAD_FLAG:
        # Connect database
        try:
            db_con = pymysql.connect(host=config.get('db', 'host'),
                                     user=config.get('db', 'user'),
                                     password=config.get('db', 'pass'),
                                     database=config.get('db', 'db'))
            while not STOP_MYSQL_THREAD_FLAG:
                if not q.empty():
                    _query = q.get()
                    with db_con.cursor() as _c:
                        _c.execute(_query)
                    db_con.commit()
                else:
                    time.sleep(1)
        except pymysql.err.OperationalError:
            time.sleep(2)


if __name__ == "__main__":
    # Load the config
    if not os.path.exists('./config.ini'):
        print('No config file!')
        sys.exit(1)

    config = configparser.ConfigParser()
    config.read('./config.ini')

    SENSORS_COUNT = config.getint('sensors', 'count')
    _tmp = config.get('sensors', 'rpm_to_airflow')
    RPM_TO_AIRFLOW_COEFFICIENTS = json.loads(_tmp)

    PIN_S0 = config.getint('gpio', 'address_0')
    PIN_S1 = config.getint('gpio', 'address_1')
    PIN_S2 = config.getint('gpio', 'address_2')
    PIN_EN = config.getint('gpio', 'enable')

    # Setup hardware
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(PIN_S0, GPIO.OUT)
    GPIO.setup(PIN_S1, GPIO.OUT)
    GPIO.setup(PIN_S2, GPIO.OUT)
    GPIO.setup(PIN_EN, GPIO.OUT)

    # Setup UART
    uart = serial.Serial(port=config.get('uart', 'uart'), baudrate=config.getint('uart', 'baudrate'),
                         xonxoff=False, rtscts=False, timeout=1)

    # Enable the multiplexor IC. Inverted logic!
    GPIO.output(PIN_EN, GPIO.HIGH)

    # Setup a queue to push mysql queries
    queries_queue = queue.Queue()

    # Start the mysql queries process
    mysql_thread = threading.Thread(target=mysql_thread_func, args=(config, queries_queue))
    mysql_thread.start()

    # Loop reading and saving
    try:
        while True:
            _sql_insert_values = []
            for i in range(0, SENSORS_COUNT):
                set_slave_address(i)
                uart.flushInput()
                # time.sleep(0.1)
                # Wait for S symbol - frame start
                uart.read_until(terminator=b'\x53', size=20)
                # Wait for E symbol - frame end
                _l = uart.read_until(terminator=b'\x45', size=20)
                _parsed = False
                _rpm = 0
                _temp = 0
                if _l and len(_l) > 1:
                    try:
                        _str = _l[:-1].decode('ASCII')
                        if _str and len(_str) > 1:
                            _ch = _str.split(',')
                            if len(_ch) is 2:
                                _rpm = float(_ch[0])
                                _temp = float(_ch[1])
                                _parsed = True
                    except:
                        _parsed = False
                if _parsed:
                    # print('S%d RPM: %d Temp: %.2f' % (i, _rpm, _temp))
                    _airflow = RPM_TO_AIRFLOW_COEFFICIENTS[i] * _rpm
                    # _last_readings[i] = {'temp': _temp, 'rpm': _rpm, 'airflow': _airflow}
                    if _temp > -127:
                        _sql_insert_values.append('(now(), %d, %.2f, %.2f, %.2f)' % (i, _temp, _rpm, _airflow))
                # else:
                # print('S%d ERR' % i)

            # with db_connection.cursor() as cr:
            #     cr.execute('insert into sensors_data (ts, sensor, temperature, rpm, airflow) values ' +
            #                ','.join(_sql_insert_values))
            # db_connection.commit()
            if len(_sql_insert_values):
                _q = 'insert into sensors_data (ts, sensor, temperature, rpm, airflow) values ' + \
                     ','.join(_sql_insert_values)
                queries_queue.put(_q)
    except KeyboardInterrupt:
        print("Signal received")
    print('Shutting down')
    STOP_MYSQL_THREAD_FLAG = True
    mysql_thread.join(2)
