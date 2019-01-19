# compatibility imports
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

# standard python includes
from bs4 import BeautifulSoup
from urllib.request import urlopen
import dbi
from log import log


def get_wu_pws(station_id):
    url = 'https://www.wunderground.com/personal-weather-station/dashboard?ID={}'.format(station_id)
    html = urlopen(url)
    return html


def validate_wx_measurement(wx):
    req_fields = {'temperature', 'humidity', 'pressure', 'precip_rate', 'dewpoint',
                  'wind_dir', 'wind_gust_speed', 'precip_today', 'feelslike'}

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
            v = v.strip()
            if v:
                try:
                    new_wx[k] = float(v)
                except ValueError:
                    msg = 'key="{}", value="{}"'.format(k, v)
                    if 'station' in wx:
                        msg += ', station={}'.format(wx['station'])
                    log(msg, error=True)
            else:
                log('parameter: {} for station: {} is blank'.format(k, wx['station']), error=True)
                new_wx[k] = -1.0

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
    """
    Get a dict of the weather attributes for station

    Since it is likely that the weather underground format will change we want to
    try and log errors and keep the intermediate information around for debugging.
    """
    failed = False
    try:
        html_text = get_wu_pws(station)
    except Exception as e:
        log('Could not get html for station {}'.format(station), error=True)
        log('    msg="{}"'.format(e), error=True)
        return False

    try:
        wx = get_weather_data(html_text)
        wx = validate_wx_measurement(wx)
    except Exception as e:
        log('Got text for station {} but it did not parse'.format(station), error=True)
        log('    msg="{}"'.format(e), error=True)
        log('    wx="{}"'.format(wx), error=True)
        failed = True

    if (not wx) or failed:
        # need to write html_text to a debug file
        with open('failed.html', 'w') as fp:
            fp.write(html_text)

    return wx

