# -*- coding: utf-8 -*-
import get_reading
import datetime
import json


# --------------  class to overrite sending of email.
def email_to_file(subject: str, body: str, body_type: str='text'):
    with open('email_output.txt', 'w') as fp:
        print(f'Subject: {subject}', file=fp)
        print(f'\n{body}', file=fp)


def email_file_to_str():
    with open('email_output.txt') as fp:
        return fp.read()


def get_test_dir(date):
    return './testdata'


# -------------  start of tests

def test_pm_send_mail(monkeypatch):
    monkeypatch.setattr(get_reading, "pm_send_message", email_to_file)
    get_reading.pm_send_message('test email', 'hello')
    txt = email_file_to_str()
    assert 'test email' in txt
    assert 'hello' in txt


def test_get_data_dir():
    dir_name = get_reading.get_data_dir('2019-01-01')
    assert dir_name.startswith('./data')
    assert '2019' in dir_name
    dir_name = get_reading.get_data_dir('2020-01-01')
    assert '2020' in dir_name


def test_test_dir_name(monkeypatch):
    monkeypatch.setattr(get_reading, "get_data_dir", get_test_dir)
    dir_name = get_reading.get_data_dir('2019-01-01')
    assert dir_name == './testdata'


def test_send_daily_summary(monkeypatch):
    monkeypatch.setattr(get_reading, "pm_send_message", email_to_file)
    get_reading.send_daily_summary('2019-08-30')  # data we have test data for
    msg = email_file_to_str()
    assert 'highest temperature today' in msg
    assert 'rain' in msg
    assert 'wind gust' in msg
    assert 'Calado' in msg
    assert 'Palo Santo' in msg
