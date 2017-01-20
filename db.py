# compatibility imports
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

# standard python includes
import os
import sys
import datetime
import pytz

from pony import orm
from pony.orm import Required, Optional
import dj_database_url


db = orm.Database()


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
        print(wx_data)
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


def db_bind():
    global db

    connect_string = dj_database_url.config()
    if connect_string['ENGINE'] == 'django.db.backends.postgresql_psycopg2':
        db_name = 'postgres'
    elif connect_string['ENGINE'] == 'django.db.backends.sqlite3':
        db_name = 'sqlite'
    else:
        print('Invalid DATABASE_URL, database not recognized: {}'.format(os.environ['DATABASE_URL']))
        assert False

    if db_name == 'postgres':
        host = connect_string['HOST']
        passwd = connect_string['PASSWORD']
        database = connect_string['NAME']
        uname = connect_string['USER']
        print('Connecting to {} with uname={} and p={}'.format(host, uname, passwd))
        db.bind('postgres', user=uname, host=host, database=database)

    elif db == 'sqlite':
        filename = connect_string['NAME']
        db.bind('sqlite', filename, create_db=True)
    else:
        print('Invalid DATABASE_URL: {}'.format(connect_string))
        assert False
    db.generate_mapping(create_tables=True)


@orm.db_session
def add_wu_reading(wx):
    Reading.from_wunderground(wx)
    orm.commit()


def make_tables():
    db.generate_mapping(create_tables=True)

