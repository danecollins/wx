from typing import List
import os
import json
import datetime
import pandas as pd  # type: ignore
import glob
from postmarker.core import PostmarkClient  # type: ignore
from wu_int import get_station_data, STATION_LIST, Reading
from log import log
from time import sleep
import pytz

# import twilio
# from twilio.rest import TwilioRestClient

# Postmarker library - https://github.com/Stranger6667/postmarker/
# docs - https://postmarker.readthedocs.io/en/stable/
token = os.environ['PM_TOKEN']


def pm_send_message(subject: str, body: str, body_type: str='text') -> None:
    """ send an email through Postmark service """
    postmark = PostmarkClient(server_token=token)
    log(f'Emailing with subject "{subject}"')
    try:
        if body_type == 'text':
            return postmark.emails.send(From='dane@dacxl.com', To='dane@dacxl.com', Subject=subject, TextBody=body)
        else:
            return postmark.emails.send(From='dane@dacxl.com', To='dane@dacxl.com', Subject=subject, HtmlBody=body)
    except Exception as e:
        log('Caught exception sending email:')
        log(e)


def write_readings_json(readings: List[Reading], filename: str) -> None:
    with open(filename, 'w') as fp:
        fp.write(json.dumps([x.to_dict() for x in readings], indent=4))


def write_readings_parquet(readings: List[Reading], filename: str) -> None:
    """ write a list of readings to file, cheating a little with __dict__ """
    data = [x.to_dict() for x in readings]
    df = pd.DataFrame.from_records(data)
    df.to_parquet(filename)
    log(f'Readings logged to {filename}')


def readings_to_file(fn: str, format: str='json') -> None:
    """ iterate through stations, get the data and write to a file """
    station_ids = list(STATION_LIST.keys())
    retry_count = 3

    readings = []
    while retry_count > 0:
        for station in station_ids:
            data = get_station_data(station)
            if data:
                readings.append(data)
                station_ids.remove(station)
                # check rain for a limited set of stations
                if STATION_LIST[station].rain:
                    check_rain(station, data.precip_today)
            sleep(2)
        retry_count -= 1

    if len(station_ids) > 0:
        log('Could not get readings for these stations: {}'.format(','.join(station_ids)))

    if format == 'json':
        write_readings_json(readings, fn)
    elif format == 'parquet':
        write_readings_parquet(readings, fn)
    else:
        raise ValueError(f'Illegal format "{format}"')


def get_data_dir(date: str) -> str:
    """ retrieve data directory in a testable way """
    return f'./data/{date[:4]}'


def read_day(date: str):
    """ load all data for a given day into a dataframe """
    data_dir = get_data_dir(date)
    pattern = f'{data_dir}/wx_{date}*.pq'
    files = glob.glob(pattern)
    data = [pd.read_parquet(f) for f in files]
    df = pd.concat(data)
    return df


def send_daily_summary(date: str) -> None:
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

    max_values = df.groupby('name').agg(max)[['temperature', 'precip_today']]
    msg = f"""
This is the daily summary for {date}

The highest temperature today was {high_temp} at station {high_loc}.
{rain_msg}
The highest wind gust was {wind_high} mph at station {wind_loc}.

The max values by location were:

{max_values}

message sent from get_reading.py
"""
    print(msg)
    pm_send_message('Daily weather summary', msg, body_type='text')


if __name__ == '__main__':
    # want logging in local time so end-of-day is understandable
    # this needs to be fixed if we have east coast stations
    tz = pytz.timezone('US/Pacific')
    time = datetime.datetime.now(tz)

    fn = time.strftime('wx_%Y-%m-%d_%H%M%S.pq')
    data_dir = get_data_dir(str(time))
    pathname = f'{data_dir}/{fn}'
    readings_to_file(pathname, format='parquet')
    if time.hour >= 21:
        send_daily_summary(time.strftime('%Y-%m-%d'))
        log(f'emailed weather stats at {time.hour:02d}:{time.minute:02d}.')
