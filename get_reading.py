# -*- coding: utf-8 -*-
from typing import List
import os
import json
import datetime
import pandas as pd

import twilio
from twilio.rest import TwilioRestClient

from wu_int import get_station_data, STATION_LIST
from log import log

def write_readings_json(readings: List["Reading"], filename: str) -> None:
    with open(filename, 'w') as fp:
        fp.write(json.dumps([x.to_dict() for x in readings], indent=4))


def write_readings_parquet(readings: List["Reading"], filename: str) -> None:
    data = [x.to_dict() for x in readings]
    df = pd.DataFrame.from_records(data)
    df.to_parquet(filename)


def readings_to_file(fn: str, format: str='json') -> None:
    station_ids = list(STATION_LIST.keys())

    readings = [get_station_data(station) for station in station_ids]
    if format == 'json':
        write_readings_json(readings, fn)
    elif format == 'parquet':
        write_readings_parquet(readings, fn)
    else:
        raise(ValueError, f'Illegal format "{format}"')


def check_rain():
    station_ids = [('KCASANJO644', 'Home'),
                   ('KCASANTA746', 'Beach'),
                   ('KORPORTL125', 'Portland')]
    for station, desc in station_ids:
        incr = Reading.check_for_increase(station)
        if incr:
            msg = 'Rain has reached {} inches at station {}'.format(incr, desc)
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
    time = datetime.datetime.now()
    #fn = time.strftime('wx_%Y-%m-%d_%H%M%S.json')
    #readings_to_file(fn)
    fn = time.strftime('wx_%Y-%m-%d_%H%M%S.pq')
    readings_to_file(fn, format='parquet')
