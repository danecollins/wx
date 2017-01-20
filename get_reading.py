import unittest
from wu_int import get_station_data
from db import db_bind, add_wu_reading


def get_readings():
    station_ids = ['KCASANJO644', 'KCASANTA746', 'KCONIWOT9']
    db_bind()

    for station in station_ids:
        wx = get_station_data(station)
        if wx:
            add_wu_reading(wx)
        else:
            print('Could not get weather for {}'.format(station))


if __name__ == '__main__':
    get_readings()