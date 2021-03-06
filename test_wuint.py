# -*- coding: utf-8 -*-
from wu_int import get_pws_data, Reading
import datetime
import json


# -------------  other support functions
def read_text_file(fn):
    with open(fn) as fp:
        text = fp.read()
    return text


def read_json_file(fn):
    text = read_text_file(fn)
    return json.loads(text)


# -------------  start of tests
def test_get_none_values():
    text = read_text_file('testdata/none_values.txt')
    data = get_pws_data('station_name', html_text=text)
    obj = Reading.from_dict(data)
    assert obj.precip_rate == 0.0
    assert obj.wind_gust_speed is None
    assert obj.precip_today == 0.0
