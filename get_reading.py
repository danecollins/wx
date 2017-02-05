
import os

import twilio
from twilio.rest import TwilioRestClient

from wu_int import get_station_data
from db import db_bind, add_wu_reading, Reading
from pony.orm import select, db_session, desc

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

    for station in station_ids:
        wx = get_station_data(station)
        if wx:
            add_wu_reading(wx)
            log('Add weather reading for {}'.format(station))
        else:
            log('Could not get weather for {}'.format(station), error=True)


def check_rain():
    station_ids = ['KCASANJO644', 'KCASANTA746']
    for station in station_ids:
        incr = Reading.check_for_increase(station)
        if incr:
            msg = 'Rain has reached {} inches at station {}'.format(incr, station)
            log(msg)
            sms(msg)


def sms(msg):
    account_sid = os.environ.get('TWILIO_ACCOUNT_SID') or 'ACCOUNT_MISSING'
    auth_token = os.environ.get('TWILIO_AUTH_TOKEN') or 'AUTH_TOKEN_MISSING'
    client = TwilioRestClient(account_sid, auth_token)
    try:
        client.messages.create(to='+14086790481', from_='+16692214546', body=msg)
        log('sms: ' + msg)
    except twilio.TwilioRestException as e:
        m = 'Twilio returned error {}'.format(e)
        log(m, error=True)


if __name__ == '__main__':
    db_bind()
    get_readings()
    check_rain()
