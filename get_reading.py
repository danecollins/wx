
import os


import twilio
from twilio.rest import TwilioRestClient

from wu_int import get_station_data
import dbi
from dbi import Reading
from log import log


def get_readings():
    station_ids = dbi.get_station_list()

    for station in station_ids:
        wx = get_station_data(station)
        if wx:
            r = Reading.add_wu_reading(wx)
            log('Add reading for {:11s} temp={} ptot={}'.format(station, r.temp, r.precip_tot))
        else:
            log('Could not get weather for {}'.format(station), error=True)


def check_rain():
    station_ids = ['KCASANJO644', 'KCASANTA746', 'KORPORTL125']
    for station in station_ids:
        incr = Reading.check_for_increase(station)
        if incr:
            msg = 'Rain has reached {} inches at station {}'.format(incr, station)
            log(msg)
            sms(msg)


def sms(msg):
    account_sid = os.environ.get('TWILIO_ACCOUNT_SID') or 'ACCOUNT_MISSING'
    auth_token = os.environ.get('TWILIO_AUTH_TOKEN') or 'AUTH_TOKEN_MISSING'
    from_num = os.environ.get('TWILIO_FROM')
    to_num = os.environ.get('TWILIO_TO')
    client = TwilioRestClient(account_sid, auth_token)
    try:
        client.messages.create(to=to_num, from_=from_num, body=msg)
        log('sms: ' + msg)
    except twilio.TwilioRestException as e:
        m = 'Twilio returned error {}'.format(e)
        log(m, error=True)


if __name__ == '__main__':
    dbi.db_bind_for_execution()
    get_readings()
    check_rain()
