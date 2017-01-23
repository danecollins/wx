import unittest
from wu_int import get_station_data
from db import db_bind, add_wu_reading

import logging
from logging.handlers import SysLogHandler

LOG_PREFIX = 'get_reading'

def ptt_logger():
    locallog = logging.getLogger()
    locallog.setLevel(logging.INFO)

    syslog = SysLogHandler(address=('logs2.papertrailapp.com', 55691))
    formatter = logging.Formatter('%(asctime)s weather %(levelname)s: %(message)s', datefmt='%Y-%m-%dT%H:%M:%S')

    syslog.setFormatter(formatter)
    locallog.addHandler(syslog)
    return locallog


logger = ptt_logger()


def log(msg, error=False, debug=False):
    global logger, LOG_PREFIX
    s = '{} - {}'.format(LOG_PREFIX, msg)
    if error:
        logger.error(s)
    elif debug:
        logger.debug(s)
    else:
        logger.info(s)


def get_readings():
    station_ids = ['KCASANJO644', 'KCASANTA746', 'KCONIWOT9']
    db_bind()

    for station in station_ids:
        wx = get_station_data(station)
        if wx:
            add_wu_reading(wx)
            log('Add weather reading for {}'.format(station))
        else:
            log('Could not get weather for {}'.format(station), error=True)


if __name__ == '__main__':
    get_readings()