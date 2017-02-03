
import os

import twilio
from twilio.rest import TwilioRestClient

from wu_int import get_station_data
from db import db_bind, add_wu_reading, Reading
from pony.orm import select, db_session, desc


@db_session
def get_readings():
    station_ids = ['KCASANJO644', 'KCASANTA746', 'KCONIWOT9']

    for station in station_ids:
        wx = get_station_data(station)
        if wx:
            add_wu_reading(wx)
        else:
            print('Could not get weather for {}'.format(station))


@db_session
def check_rain():
    station_ids = ['KCASANJO644', 'KCASANTA746']
    db_session()
    for station in station_ids:
        readings = select(r for r in Reading if r.station == station).order_by(desc(Reading.time))[:2]
        rain_in_quarter_inches = [int(4.0 * x.precip_tot) for x in readings]
        if rain_in_quarter_inches[0] != rain_in_quarter_inches[1]:
            sms('Rain has reached {} inches at station {}'.format(readings[1].precip_tot, station))
        else:
            print('No change in rain at {} inches'.format(readings[1].precip_tot))


def sms(msg):
    account_sid = os.environ.get('TWILIO_ACCOUNT_SID') or 'ACCOUNT_MISSING'
    auth_token = os.environ.get('TWILIO_AUTH_TOKEN') or 'AUTH_TOKEN_MISSING'
    client = TwilioRestClient(account_sid, auth_token)
    try:
        client.messages.create(to='+14086790481', from_='+16692214546', body=msg)
    except twilio.TwilioRestException as e:
        m = 'Twilio returned error {}'.format(e)
        print(m)


if __name__ == '__main__':
    db_bind()
    # get_readings()
    check_rain()
