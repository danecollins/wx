# compatibility imports
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

# standard python includes
import os
import sys
import datetime

from pony import orm
from pony.orm import Required, Optional

# ##### define database
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

# db.bind('sqlite', 'db.sqlite', create_db=True)
db.bind('postgres', user='dane', host='localhost', database='wx_readings')

db.generate_mapping(create_tables=True)


@orm.db_session
def add_meas():
    now = datetime.datetime.now()
    Reading(temp=50.3, humid=.34, pressure=29.45, precip_rate=0, precip_tot=.45, time=now, station='KCASANJO644')
    Reading(temp=45.0, humid=.78, pressure=30.10, precip_rate=0, precip_tot=.45, time=now, station='KCASANTA746')
    orm.commit()


add_meas()
