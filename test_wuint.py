# -*- coding: utf-8 -*-
from wu_int import get_pws_data, Reading, read_rain, write_rain, check_rain
import datetime
import json
import os

# -------------  other support functions
def read_text_file(fn):
    with open(fn) as fp:
        text = fp.read()
    return text


def read_json_file(fn):
    text = read_text_file(fn)
    return json.loads(text)


def rain_test_generator():
    records = [
    '{"observations": [{"stationID": "KCASANJO644", "obsTimeUtc": "2019-08-29T23:00:26Z", "obsTimeLocal": "2019-08-29 16:00:26", "neighborhood": "West Campbell", "softwareType": "weatherlink.com 1.10", "country": "US", "solarRadiation": 0, "lon": -121.98395538, "realtimeFrequency": 0, "epoch": 1567119626, "lat": 37.28738403, "uv": 0, "winddir": 359, "humidity": 60, "qcStatus": 1, "imperial": {"temp": 78, "heatIndex": 78, "dewpt": 63, "windChill": 78, "windSpeed": 5, "windGust": 12, "pressure": 29.84, "precipRate": 0.10, "precipTotal": 0.10, "elev": 0}}]}',
     '{"observations": [{"stationID": "KCASANJO644", "obsTimeUtc": "2019-08-29T23:00:26Z", "obsTimeLocal": "2019-08-29 16:00:26", "neighborhood": "West Campbell", "softwareType": "weatherlink.com 1.10", "country": "US", "solarRadiation": 0, "lon": -121.98395538, "realtimeFrequency": 0, "epoch": 1567119626, "lat": 37.28738403, "uv": 0, "winddir": 359, "humidity": 60, "qcStatus": 1, "imperial": {"temp": 78, "heatIndex": 78, "dewpt": 63, "windChill": 78, "windSpeed": 5, "windGust": 12, "pressure": 29.84, "precipRate": 0.10, "precipTotal": 0.20, "elev": 0}}]}',
     '{"observations": [{"stationID": "KCASANJO644", "obsTimeUtc": "2019-08-29T23:00:26Z", "obsTimeLocal": "2019-08-29 16:00:26", "neighborhood": "West Campbell", "softwareType": "weatherlink.com 1.10", "country": "US", "solarRadiation": 0, "lon": -121.98395538, "realtimeFrequency": 0, "epoch": 1567119626, "lat": 37.28738403, "uv": 0, "winddir": 359, "humidity": 60, "qcStatus": 1, "imperial": {"temp": 78, "heatIndex": 78, "dewpt": 63, "windChill": 78, "windSpeed": 5, "windGust": 12, "pressure": 29.84, "precipRate": 0.10, "precipTotal": 0.30, "elev": 0}}]}',
     '{"observations": [{"stationID": "KCASANJO644", "obsTimeUtc": "2019-08-29T23:00:26Z", "obsTimeLocal": "2019-08-29 16:00:26", "neighborhood": "West Campbell", "softwareType": "weatherlink.com 1.10", "country": "US", "solarRadiation": 0, "lon": -121.98395538, "realtimeFrequency": 0, "epoch": 1567119626, "lat": 37.28738403, "uv": 0, "winddir": 359, "humidity": 60, "qcStatus": 1, "imperial": {"temp": 78, "heatIndex": 78, "dewpt": 63, "windChill": 78, "windSpeed": 5, "windGust": 12, "pressure": 29.84, "precipRate": 0.10, "precipTotal": 0.30, "elev": 0}}]}'
     ]
    
    for r in records:
        yield r


# -------------  start of tests

# rain tests

def clear_rain(station='test_station'):
    fn = f'{station}.txt'
    if os.path.exists(fn):
        os.remove(fn)


def test_read_rain_file_missing():
    """ if the file is missing then zero should be returned """
    clear_rain('test_station')
    value = read_rain('test_station')
    assert value == 0.0


def test_write_rain():
    write_rain('test_station', 5.0)
    value = read_rain('test_station')
    assert value == 5.0


def test_rain_computation():
    station = 'KCASANJO644'
    clear_rain(station)
    gen = rain_test_generator()

    data = get_pws_data(station, html_text=next(gen))
    obj = Reading.from_dict(data)
    assert not check_rain(station, obj.precip_today) 
    data = get_pws_data(station, html_text=next(gen))
    obj = Reading.from_dict(data)
    assert not check_rain(station, obj.precip_today)
    data = get_pws_data(station, html_text=next(gen))
    obj = Reading.from_dict(data)
    assert check_rain(station, obj.precip_today)


def test_rain_reset():
    """ if rain decreases we have to be on a new day """
    station = 'KCASANJO644'
    clear_rain(station)
    gen = rain_test_generator()

    data = get_pws_data(station, html_text=next(gen))
    obj = Reading.from_dict(data)
    check_rain(station, obj.precip_today) 
    data = get_pws_data(station, html_text=next(gen))
    obj = Reading.from_dict(data)
    check_rain(station, obj.precip_today)
    data = get_pws_data(station, html_text=next(gen))
    obj = Reading.from_dict(data)
    check_rain(station, obj.precip_today)
    data = get_pws_data(station, html_text=next(gen))
    obj = Reading.from_dict(data)
    assert not check_rain(station, obj.precip_today)
    value = read_rain(station)
    assert value == obj.precip_today


# data parsing tests
def test_get_none_values():
    text = read_text_file('testdata/none_values.txt')
    data = get_pws_data('station_name', html_text=text)
    obj = Reading.from_dict(data)
    assert obj.precip_rate == 0.0
    assert obj.wind_gust_speed is None
    assert obj.precip_today == 0.0


def test_campbell_values():
    text = read_text_file('testdata/campbell_response.txt')
    data = get_pws_data('KCASANJO644', html_text=text)
    obj = Reading.from_dict(data)
    assert obj.precip_rate == 0.0
    assert obj.wind_gust_speed == 12.0
    assert obj.precip_today == 1.0


