# -*- coding: utf-8 -*-
from typing import List
import os
import json
import datetime
import pandas as pd
import glob
from postmarker.core import PostmarkClient
from wu_int import get_station_data, STATION_LIST
from log import log

# import twilio
# from twilio.rest import TwilioRestClient

# Postmarker library - https://github.com/Stranger6667/postmarker/
# docs - https://postmarker.readthedocs.io/en/stable/
token = os.environ['PM_TOKEN']


def pm_send_message(subject: str, body: str, body_type: str='text') -> None:
    postmark = PostmarkClient(server_token=token)
    if body_type == 'text':
        return postmark.emails.send(From='dane@dacxl.com', To='dane@awr.com', Subject=subject, TextBody=body)
    else:
        return postmark.emails.send(From='dane@dacxl.com', To='dane@awr.com', Subject=subject, HtmlBody=body)


def write_readings_json(readings: List["Reading"], filename: str) -> None:
    with open(filename, 'w') as fp:
        fp.write(json.dumps([x.to_dict() for x in readings], indent=4))


def write_readings_parquet(readings: List["Reading"], filename: str) -> None:
    data = [x.to_dict() for x in readings]
    df = pd.DataFrame.from_records(data)
    df.to_parquet(filename)
    log(f'Readings logged to {filename}')


def readings_to_file(fn: str, format: str='json') -> None:
    station_ids = list(STATION_LIST.keys())

    readings = [get_station_data(station) for station in station_ids]
    if format == 'json':
        write_readings_json(readings, fn)
    elif format == 'parquet':
        write_readings_parquet(readings, fn)
    else:
        raise(ValueError, f'Illegal format "{format}"')


def read_day(date):
    pattern = f'./data/{date[:4]}/wx_{date}*.pq'
    files = glob.glob(pattern)
    print(files)
    data = [pd.read_parquet(f) for f in files]
    df = pd.concat(data)
    return df


def send_daily_summary(date):
    df = read_day(date)
    r = df.sort_values(['temperature', 'feelslike'], ascending=False).iloc[0]
    high_temp = r.temperature
    high_loc = r['name']

    r = df.sort_values(['precip_today', 'precip_rate'], ascending=False).iloc[0]
    if r.precip_today == 0.0:
        rain_msg = 'There was no rain today.'
    else:
        rain_msg = f'There was a total of {r.precip_today}" rain at station {r["name"]}.'
    
    r = df.sort_values(['wind_gust_speed'], ascending=False).iloc[0]
    wind_high = r.wind_gust_speed
    wind_loc = r['name']
    msg = f"""
This is the daily summary for {date}

The highest temperature today was {high_temp} at station {high_loc}.
{rain_msg}
The highest wind gust was {wind_high} mph at station {wind_loc}.


message sent from get_reading.py
"""
    print(msg)
    pm_send_message('Daily weather summary', msg, body_type='text')



# def check_rain():
#     station_ids = [('KCASANJO644', 'Home'),
#                    ('KCASANTA746', 'Beach'),
#                    ('KORPORTL125', 'Portland')]
#     for station, desc in station_ids:
#         incr = Reading.check_for_increase(station)
#         if incr:
#             msg = 'Rain has reached {} inches at station {}'.format(incr, desc)
#             log(msg)
#             sms(msg)


# def sms(msg):
#     account_sid = os.environ.get('TWILIO_ACCOUNT_SID') or 'ACCOUNT_MISSING'
#     auth_token = os.environ.get('TWILIO_AUTH_TOKEN') or 'AUTH_TOKEN_MISSING'
#     from_num = os.environ.get('TWILIO_FROM')
#     to_num = os.environ.get('TWILIO_TO')
#     client = TwilioRestClient(account_sid, auth_token)
#     try:
#         client.messages.create(to=to_num, from_=from_num, body=msg)
#         log('sms: ' + msg)
#     except twilio.TwilioRestException as e:
#         m = 'Twilio returned error {}'.format(e)
#         log(m, error=True)


if __name__ == '__main__':
    time = datetime.datetime.now()
    #fn = time.strftime('wx_%Y-%m-%d_%H%M%S.json')
    #readings_to_file(fn)
    fn = time.strftime('wx_%Y-%m-%d_%H%M%S.pq')
    pathname = f'./data/{time.year}/{fn}'
    readings_to_file(pathname, format='parquet')
    if time.hour >= 20:
        send_daily_summary(time.strftime('%Y-%m-%d'))

