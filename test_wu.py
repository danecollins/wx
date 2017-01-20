import unittest
from wu_int import get_weather_data, validate_wx_measurement

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
        

if __name__ == '__main__':
    unittest.main()