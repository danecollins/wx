import unittest

from wu_int import get_weather_data, validate_wx_measurement
import dbi
from dbi import Reading
from pony.orm import db_session, select

dbi.db_bind_for_test()


class TestWuParse(unittest.TestCase):
    def test_parse_page(self):
        with open('./testdata/pws_ex1.html') as fp:
            html_text = fp.read()

        wx = get_weather_data(html_text)
        d = {'wind_gust_speed': '8.0', 'pressure': '29.77', 'temperature': '50.3',
             'humidity': '91', 'wind_dir': 'SE', 'precip_rate': '0.04',
             'feelslike': '50.3', 'precip_today': ' 0.43', 'dewpoint': '48'}
        for k, v in d.items():
            self.assertEqual(v, wx[k])

    def test_convert_page(self):
        with open('./testdata/pws_ex1.html') as fp:
            html_text = fp.read()

        wx = get_weather_data(html_text)
        wx = validate_wx_measurement(wx)
        d = {'wind_gust_speed': 8.0, 'pressure': 29.77, 'temperature': 50.3,
             'humidity': 91, 'wind_dir': 'SE', 'precip_rate': 0.04,
             'feelslike': 50.3, 'precip_today': 0.43, 'dewpoint': 48}
        for k, v in d.items():
            self.assertEqual(v, wx[k])


class TestDb(unittest.TestCase):
    def setup(self):
        pt1 = dict(temperature=55.0, humidity=.23, pressure=29.45,
                   wind_dir='NW', wind_gust_speed=4.3, dewpoint=65,
                   feelslike=65, precip_rate=.12, precip_today=.20,
                   station='test')
        pt2 = dict(temperature=55.0, humidity=.23, pressure=29.45,
                   wind_dir='NW', wind_gust_speed=4.3, dewpoint=65,
                   feelslike=65, precip_rate=.12, precip_today=.20,
                   station='test')
        pt3 = dict(temperature=55.0, humidity=.23, pressure=29.45,
                   wind_dir='NW', wind_gust_speed=4.3, dewpoint=65,
                   feelslike=65, precip_rate=.12, precip_today=.20,
                   station='test')
        with db_session:
            Reading.clear_all_readings()
            Reading.add_wu_reading(pt1)
            Reading.add_wu_reading(pt2)
            Reading.add_wu_reading(pt3)
        return 3

    def test_db_setup(self):
        num_created = self.setup()
        with db_session:
            record_count = Reading.select().count()
        self.assertEqual(num_created, record_count)

    def test_add_wu_reading(self):
        self.setup()
        with db_session:
            obj = select(p for p in Reading)[:][0]
            self.assertEqual(obj.temp, 55.0)
            self.assertEqual(obj.wind_dir, 'NW')

    def test_check_for_increase(self):
        self.setup()
        self.assertFalse(Reading.check_for_increase('test'))
        # this point crosses total
        pt = dict(temperature=55.0, humidity=.23, pressure=29.45,
                  wind_dir='NW', wind_gust_speed=4.3, dewpoint=65,
                  feelslike=65, precip_rate=.12, precip_today=.30,
                  station='test')
        with db_session:
            Reading.add_wu_reading(pt)
            num_readings = Reading.select().count()
        self.assertEqual(0.30, Reading.check_for_increase('test'))
        self.assertEqual(4, num_readings)


if __name__ == '__main__':
    unittest.main()
