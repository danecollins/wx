from dbi import Reading, make_tables, db_bind_from_url
import datetime


db_bind_from_url()
make_tables()

start_day = datetime.date(2017, 1, 21)
end_day = datetime.date(2018, 10, 31)

current = start_day

while current <= end_day:
    day_str = current.strftime('wx_data/wx_%Y-%m-%d.json')
    print('Writing to {}'.format(day_str))
    with open(day_str, 'w') as fp:
        fp.write(Reading.day_to_json(current))
        current += datetime.timedelta(days=1)

