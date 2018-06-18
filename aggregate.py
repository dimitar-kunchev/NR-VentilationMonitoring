#!/usr/bin/python3
"""
Sensors aggregation and storage.
https://github.com/dimitar-kunchev/NR-VentilationMonitoring
@author: Dimitar Kunchev
@license: See the LICENSE file
@email: dimitar.kunchev@racecloud.net
"""
import pymysql
import configparser
import getopt
import sys
import warnings


if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read('./config.ini')

    try:
        opts, args = getopt.getopt(sys.argv[1:], 'm:', ['mode='])
    except getopt.GetoptError as e:
        print(e)
        sys.exit(2)

    mode = None
    for o, a in opts:
        if o in ('-m', '--mode'):
            mode = a
        else:
            assert False, 'unhandled option'

    if mode is None:
        assert False, 'mode not specified (use -m or --mode)'

    output_table = None
    interval = None

    if mode == '5m':
        output_table = '5min'
        interval = '5 minute'
    elif mode == '1h':
        output_table = '1hour'
        interval = '60 minute'
    elif mode == '1d':
        output_table = '1day'
        interval = '24 hour'
    elif mode == 'cleanup':
        pass
    else:
        assert False, 'invalid mode (must be 5m, 1h or 1d)'

    warnings.filterwarnings('ignore', category=pymysql.Warning)

    db_connection = pymysql.connect(host=config.get('db', 'host'),
                                    user=config.get('db', 'user'),
                                    password=config.get('db', 'pass'),
                                    database=config.get('db', 'db'))

    with db_connection.cursor() as c:
        if mode == 'cleanup':
            c.execute('delete from sensors_data where ts < date_sub(now(), interval 2 day)')
            c.execute('delete from sensors_data_5min where ts < date_sub(now(), interval 2 day)')
            c.execute('delete from sensors_data_1hour where ts < date_sub(now(), interval 7 day)')
        else:
            c.execute('insert into sensors_data_' + output_table + ' ' +
                      '(ts, sensor, rpm, temperature, airflow) '
                      'select now(), sensor, avg(rpm), avg(temperature), avg(airflow) from sensors_data '
                      'where ts > date_sub(now(), interval ' + interval + ') group by sensor')
    db_connection.commit()
