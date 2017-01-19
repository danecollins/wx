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
import pandas as pd


def get_page():
    with open('./testdata/pws_ex1.html') as fp:
        html_text = fp.read()

    return html_text


def get_wu_pws(station_id):
    url = 'https://www.wunderground.com/personal-weather-station/dashboard?ID={}'.format(station_id)
    html = urlopen(url)
    return html


def test_wx_measurement(wx):
    req_fields = {'temperature', 'humidity', 'pressure', 'precip_rate', 'dewpoint', 'wind_dir', 'wind_gust_speed', 
                  'precip_today', 'feelslike'}

    k = wx.keys()

    if req_fields - k:
        print('The following keys were not found {}'.format(req_fields - k))
        return False
    else:
        return True


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

    return wx

if __name__ == '__main__':
    station_ids = ['KCASANJO644', 'KCASANTA746', 'KCONIWOT9']
    data = {}
    for si in station_ids:
        text = get_wu_pws(si)
        wx = get_weather_data(text)
        test_wx_measurement(wx)
        data[si] = wx

    df = pd.DataFrame(data)
    print(df)


