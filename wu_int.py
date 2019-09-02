# -*- coding: future_fstrings -*-

# standard python includes
from typing import Dict, Any, Optional
import requests
import os
import datetime
import re
import json

# my packages
from log import log

nan = float('nan')
TIME_PATTERN = re.compile('([0-9]+) minutes ago')

# this is the list of stations we want weather for.  Add a station here to start collecting data
STATION_LIST = {
    'KCASANJO644': dict(name='Palo Santo', rain=True),
    'KCASANTA746': dict(name='Harbor', rain=True),
    'KCONIWOT9': dict(name='Niwot', rain=False),
    'KCASANTA78': dict(name='Saratoga', rain=False),
    'KCACAMPB54': dict(name='Calado', rain=False),
    'KORPORTL125': dict(name='NW Portland', rain=False),
    'KORPORTL1314': dict(name='Pearl District', rain=False),
}


class Reading:
    """ validate that all variables of interest were found """
    temperature = nan  # type: float
    humidity = nan  # type: float
    pressure = nan  # type: float
    precip_rate = 0.0  # type: float
    dewpoint = nan  # type: float
    wind_dir = None  # type: int
    wind_gust_speed = nan  # type: float
    precip_today = 0.0  # type: float
    feelslike = nan  # type: float
    station = None  # type: str
    timestamp = None  # type: str
    name = None  # type: str

    @classmethod
    def from_dict(cls, data: Dict) -> "Reading":
        self = cls()

        self.station = data['stationID']
        self.name = str(STATION_LIST[self.station]['name'])
        self.timestamp = data['obsTimeLocal']
        m = data['imperial']
        self.temperature = m['temp']
        self.dewpoint = m['dewpt']
        self.feelslike = m['windChill']
        self.wind_gust_speed = m['windGust']
        self.pressure = m['pressure']
        self.precip_rate = m['precipRate'] or self.precip_rate
        self.precip_today = m['precipTotal'] or self.precip_today
        self.wind_dir = data['winddir']
        self.humidity = data['humidity']
        return self

    def to_dict(self):
        return self.__dict__


def get_pws_data(sid: str, html_text: str=None, write_data: bool=False) -> Optional[Dict[str, Any]]:
    """
    url format: https://api.weather.com/v2/pws/observations/current?stationId=KCASANJO644&
                format=json&units=e&apiKey=455d77d904354fb79d77d904356fb76b

    return value:
    {"observations":[{"stationID":"KCASANJO644","obsTimeUtc":"2019-08-29T22:45:25Z",
     "obsTimeLocal":"2019-08-29 15:45:25","neighborhood":"West Campbell",
     "softwareType":"weatherlink.com 1.10","country":"US","solarRadiation":null,
     lon":-121.98395538,"realtimeFrequency":null,"epoch":1567118725,
     "lat":37.28738403,"uv":null,"winddir":336,"humidity":60,"qcStatus":1,
     "imperial":{"temp":78,"heatIndex":78,"dewpt":63,"windChill":78,
     "windSpeed":6,"windGust":11,"pressure":29.84,"precipRate":0.00,
     "precipTotal":0.00,"elev":0}}]}
    """
    key = os.environ['WU_API_KEY']
    url = f'http://api.weather.com/v2/pws/observations/current?stationId={sid}&format=json&units=e&apiKey={key}'

    if html_text is None:
        result = requests.get(url)
        if result.status_code != 200:
            print(f'Could not get html page')
            print(f'URL: {url}')
            print(f'Status Code: {result.status_code}, Reason: {result.reason}')
            print(result.__dict__)
            log(f'Station {sid} returned web code {result.status_code}.', error=True)
            return None
        else:
            html_text = result.text

    if write_data:
        with open('html_text.txt', 'w') as fp:
            fp.write(html_text)
            fp.write('\n')

    raw_data = json.loads(html_text)
    observation = raw_data['observations'][0]
    return observation


def get_station_data(station: str, html_text: str=None) -> Optional["Reading"]:
    """
    Get a Reading of the weather attributes for station

    Since it is likely that the weather underground format will change we want to
    try and log errors and keep the intermediate information around for debugging.

    html_text can be passed in for testing the rest of the code.
    """
    print(f'Getting data for {station}')

    data = get_pws_data(station, html_text)
    if data:
        return Reading.from_dict(data)
    else:
        return None


if __name__ == '__main__':
    station = 'KORPORTL125'
    data = get_station_data(station)
    print(data)
    print()
