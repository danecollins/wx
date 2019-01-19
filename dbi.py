# standard python includes
import os
import sqlite3
import datetime
import pytz
import json

from pony import orm
from pony.orm import Required, Optional, db_session


db = orm.Database()


def db_bind_for_test():
    """ Create a database in memory for testing purposes """
    global db
    db.bind('sqlite', ':memory:')
    make_tables()
    return db


def db_bind_for_execution():
    """ Bind to database based on the DATABASE_URL string """
    global db
    db_file = './weather_readings.sqlite'
    if not os.path.exists(db_file):
        conn = sqlite3.connect(db_file)
        conn.close()
    db.bind('sqlite', db_file)
    make_tables()
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
                   precip_rate=max(wx_data['precip_rate'], 0),
                   precip_tot=max(wx_data['precip_today'], 0),  # returns -1 sometimes
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

            # handle negative values that exist due to missing readings
            readings = [max(x, 0) for x in readings]
            
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
