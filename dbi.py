# compatibility imports
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

# standard python includes
import os
import sys
import datetime
import pytz
import json

from pony import orm
from pony.orm import Required, Optional, db_session
import dj_database_url


db = orm.Database()


def db_bind_for_test():
    """ Create a database in memory for testing purposes """
    global db
    db.bind('sqlite', ':memory:')
    make_tables()
    return db


def db_bind_from_url():
    """ Bind to database based on the DATABASE_URL string """
    global db

    connect_string = dj_database_url.config()
    if connect_string['ENGINE'] == 'django.db.backends.postgresql_psycopg2':
        db_name = 'postgres'
    elif connect_string['ENGINE'] == 'django.db.backends.sqlite3':
        db_name = 'sqlite'
    else:
        print('Invalid DATABASE_URL, database not recognized: {}'.format(connect_string))
        print('engine string is "{}"'.format(connect_string['ENGINE']))
        assert False

    if db_name == 'postgres':
        host = connect_string['HOST']
        passwd = connect_string['PASSWORD']
        database = connect_string['NAME']
        uname = connect_string['USER']
        print('Connecting to {} with uname={} and p={}'.format(host, uname, passwd))
        db.bind('postgres', user=uname, host=host, password=passwd, database=database)
        make_tables()
    elif db_name == 'sqlite':
        db_bind_for_test()
    else:
        print('Invalid DATABASE_URL: {}'.format(connect_string))
        assert False

    return db


def make_tables():
    """ Create tables """
    global db
    try:
        db.generate_mapping(create_tables=True)
    except:
        # mapping must already exist
        pass


class Reading(db.Entity):
    temp = Required(float)
    humid = Required(float)
    pressure = Required(float)
    wind_dir = Optional(str)
    wind_gust_speed = Optional(float)
    dewpoint = Optional(float)
    feels_like = Optional(float)
    precip_rate = Required(float)
    precip_tot = Required(float)
    time = Required(datetime.datetime)
    station = Required(str)

    @classmethod
    def from_wunderground(cls, wx_data):
        now = datetime.datetime.now(pytz.timezone('US/Pacific'))
        # print(wx_data)
        self = cls(temp=wx_data['temperature'],
                   humid=wx_data['humidity'],
                   pressure=wx_data['pressure'],
                   wind_dir=wx_data['wind_dir'],
                   wind_gust_speed=wx_data['wind_gust_speed'],
                   dewpoint=wx_data['dewpoint'],
                   feels_like=wx_data['feelslike'],
                   precip_rate=wx_data['precip_rate'],
                   precip_tot=wx_data['precip_today'],
                   time=now,
                   station=wx_data['station'],
                   )
        return self

    def to_dict(self):
        x = self.time
        tm = datetime.datetime(x.year, x.month, x.day, x.hour, x.minute, x.second)
        return dict(temp=self.temp,
                    humid=self.humid,
                    pressure=self.pressure,
                    wind_dir=self.wind_dir,
                    wind_gust_speed=self.wind_gust_speed,
                    dewpoint=self.dewpoint,
                    feels_like=self.feels_like,
                    precip_rate=self.precip_rate,
                    precip_tot=self.precip_tot,
                    time=tm.isoformat(),
                    station=self.station)

    @classmethod
    def check_for_increase(cls, station):
        last_ix = 0
        prev_ix = 1
        with db_session:
            readings = orm.select(r for r in cls if r.station == station).order_by(orm.desc(cls.time))

            # keep last 2
            if readings.count() < 2:
                return False  # don't have enough readings yet

            readings = readings[:2]
            rain_in_quarter_inches = [int(4.0 * x.precip_tot) for x in readings]
            if rain_in_quarter_inches[last_ix] > rain_in_quarter_inches[prev_ix]:
                return readings[last_ix].precip_tot
            else:
                return False

    @classmethod
    def clear_all_readings(cls):
        with db_session:
            cls.select().delete()
            orm.commit()

    @classmethod
    def add_wu_reading(cls, wx):
        with db_session:
            obj = cls.from_wunderground(wx)
            orm.commit()
        return obj

    @classmethod
    def day_to_json(cls, day):
        with db_session:
            records = orm.select(d for d in Reading if d.time.date() == day)
            l = [r.to_dict() for r in records]
        return json.dumps(l, indent=4, sort_keys=True)

    def __str__(self):
        return 'Reading[id={},sta={},temp={}]'.format(self.id,
                                                      self.station,
                                                      self.temp)


def get_station_list():
    with open('stations.txt') as fp:
        stations = fp.readlines()

    return [x.strip() for x in stations]
