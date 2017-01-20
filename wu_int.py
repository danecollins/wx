# compatibility imports
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

# standard python includes
import os
import sys
from collections import Counter
from bs4 import BeautifulSoup
from urllib.request import urlopen


station_ids = ['KCASANJO644', 'KCASANTA746', 'KCONIWOT9']


def get_wu_pws(station_id):
    url = 'https://www.wunderground.com/personal-weather-station/dashboard?ID={}'.format(station_id)
    html = urlopen(url)
    return html


def validate_wx_measurement(wx):
    req_fields = {'temperature', 'humidity', 'pressure', 'precip_rate', 'dewpoint', 'wind_dir', 'wind_gust_speed', 
                  'precip_today', 'feelslike'}

    k = wx.keys()

    if req_fields - k:
        print('The following keys were not found {}'.format(req_fields - k))
        return False

    # convert types
    new_wx = {}
    for k, v in wx.items():
        if k in ['wind_dir', 'station']:
            new_wx[k] = v
        else:
            new_wx[k] = float(v)

    return new_wx


def get_weather_data(html_text, desired_station=False):
    soup = BeautifulSoup(html_text, "html.parser")
   
    # all the data is in spans with a class of 'wx-data'
    spans = soup.find_all('span', attrs={'class': "wx-data"})

    # we will return a dict of the different weather attributes
    wx = {}

    for span in spans:
        # all the data should be the same station so check that
        station = span.attrs['data-station']
        if desired_station:
            assert station == desired_station
        else:
            desired_station = station

        # what does this span contain
        variable = span.attrs['data-variable']

        # the value is in a sub-span
        value_span = span.find('span', attrs={'class': 'wx-value'})
        value = value_span.text

        wx[variable] = value

    wx['station'] = desired_station
    return wx

def get_station_data(station):
    text = get_wu_pws(station)
    wx = get_weather_data(text)
    wx = validate_wx_measurement(wx)
    return wx


if __name__ == '__main__':
    station_ids = ['KCASANJO644', 'KCASANTA746', 'KCONIWOT9']
    data = {}
    for si in station_ids:
        text = get_wu_pws(si)
        wx = get_weather_data(text)
        wx = validate_wx_measurement(wx)
        data[si] = wx




