# standard python includes
from typing import Dict, Any, Optional
import requests
import os
import datetime
import re
import json
import twilio
from twilio.rest import Client

# my packages
from log import log

DEBUG = True

nan = float('nan')
TIME_PATTERN = re.compile('([0-9]+) minutes ago')

# this is the list of stations we want weather for.  Add a station here to start collecting data
STATION_LIST = {
    'KCASANJO644': dict(name='c-Palo Santo', rain=True),
    'KCASANTA746': dict(name='s-Harbor', rain=False),
    'KCOBOULD425': dict(name='b-Naropa', rain=False),
    'KCOBOULD658': dict(name='b-Mapleton', rain=False),
    'KCASANTA3862': dict(name='s-SCYC', rain=True),
    'KCASANJO972': dict(name='c-Campbell', rain=False),
    'KMNMINNE775': dict(name='m-Minneapolis', rain=True),
    #'KORPORTL554': dict(name='p-Pearl District', rain=False),
    'KORPORTL1637': dict(name='p-NW Portland', rain=False),
    # 'KMNMINNE304': dict(name='m-Minneapolis', rain=True),
    # 'KCACAMPB54': dict(name='c-Calado', rain=False),
    # 'KORPORTL125': dict(name='p-NW Portland', rain=True),
    # 'KORPORTL1476': dict(name='p-NW Portland N', rain=True),
    # 'KORPORTL1314': dict(name='p-Pearl District', rain=False),
    # 'KCONIWOT9': dict(name='z-Niwot', rain=False),
}

def sms(msg):
    account_sid = os.environ.get('TWILIO_ACCOUNT_SID') or 'ACCOUNT_MISSING'
    auth_token = os.environ.get('TWILIO_AUTH_TOKEN') or 'AUTH_TOKEN_MISSING'
    client = Client(account_sid, auth_token)
    try:
        client.messages.create(to='+14086790481', from_='+16692214546', body=msg)
    except twilio.TwilioRestException as e:
        m = 'Twilio returned error {}'.format(e)
        print(m)


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
    
        if DEBUG:
            log(f'{self.name} - rate: {self.precip_rate}, total: {self.precip_today}')

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
            print(f'Got data for station {sid}')
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


def read_rain(station):
    try:
        with open(f'{station}.txt') as fp:
            rain = float(fp.readline())
    except:
        rain = 0

    return rain


def write_rain(station, value):
    with open(f'{station}.txt', 'w') as fp:
        print(value, file=fp)


def check_rain(station, current_rain):
    last_rain = read_rain(station)
    if current_rain < last_rain:  # need to reset, new day
        # reset the counter
        log(f'resetting rain total to {current_rain} in station {station}')
        write_rain(station, current_rain)
        return False

    if current_rain > (last_rain + 0.25):
        # once we trigger we set the saved level
        write_rain(station, current_rain)
        name = STATION_LIST[station]['name']
        log(f'{name} rain increased from {last_rain} to {current_rain}')
        sms(f'Rain has reached {current_rain} inches at station: {name}')
        return True
    else:
        return False


if __name__ == '__main__':
    station = 'KORPORTL125'
    data = get_station_data(station)
    print(data)
    print()
