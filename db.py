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


db = orm.Database()


class Reading(db.Entity):
    temp = Required(float)
    humid = Required(float)
    pressure = Required(float)
    wind_dir = Optional(str)
    wind_gust_speed = Optional(str)
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
    passwd = ''
    host = 'localhost'
    port = '5432'
    connect_string = os.environ['DATABASE_URL']

    db_name, path = connect_string.split(':', 1)
    if db_name == 'postgres':
        path = path[2:]  # strip //
        # postgres://dane:sjsharks@localhost:5432/wx_readings
        host_string, db_name = path.split('/')
        # print("host_string={}".format(host_string))
        # print("db_name={}".format(db_name))
        if '@' in host_string:
            user, host = host_string.split('@')
        else:
            uname = 'dane'  
        # print('user={}'.format(user))
        # print('host={}'.format(host))
        if ':' in user:
            uname, passwd = user.split(':')
        else:
            uname = 'dane'

        if ':' in host:
            host, port = host.split(':')

        # print('host={}'.format(host))
        # print('port={}'.format(port))

        print('Connecting to {} with uname={} and p={}'.format(host, uname, passwd))
        db.bind('postgres', user=uname, host=host, database='wx_readings')

    elif db == 'sqlite':
        assert path[:3] == '///'
        filename = path[3:]
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

