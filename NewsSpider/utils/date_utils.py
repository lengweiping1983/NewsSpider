# -*- coding: utf-8 -*-
import re
import datetime


def parse_datetime(source):
    try:
        match = re.search(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', source)
        if match is not None:
            return datetime.datetime.strptime(match.group(), '%Y-%m-%d %H:%M:%S')
        match = re.search(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}', source)
        if match is not None:
            return datetime.datetime.strptime(match.group(), '%Y-%m-%d %H:%M')
        match = re.search(r'\d{4}-\d{2}-\d{2} \d{2}', source)
        if match is not None:
            return datetime.datetime.strptime(match.group(), '%Y-%m-%d %H')
        match = re.search(r'\d{2}-\d{2} \d{2}:\d{2}', source)
        if match is not None:
            today = datetime.datetime.now()
            return datetime.datetime.strptime(str(today.year) + '-' + match.group(), '%Y-%m-%d %H:%M')
    except Exception as e:
        print('parse_datetime error', str(e))

    return None


def parse_date(source):
    try:
        match = re.search(r'\d{4}-\d{2}-\d{2}', source)
        if match is not None:
            return datetime.datetime.strptime(match.group(), '%Y-%m-%d')
        match = re.search(r'\d{4}\d{2}\d{2}', source)
        if match is not None:
            return datetime.datetime.strptime(match.group(), '%Y%m%d')
    except Exception as e:
        print('parse_date error', str(e))

    return None


def parse_str_get_date(source):
    date = parse_datetime(source)
    if date is None:
        date = parse_date(source)
    return date


def date_to_str(date):
    if date is not None:
        return date.strftime("%Y-%m-%d %H:%M:%S")
    return None


def timedelta_hours(hours):
    return datetime.datetime.now() + datetime.timedelta(hours=hours)


def test():
    s = "Jason's birthday is on 1991-09-21 18:22:21"
    s = "Jason's birthday is on 1991-09-21 18:22"
    s = "Jason's birthday is on 09-21 18:22"
    # s = "Jason's birthday is on 1991-09-21"
    print(parse_str_get_date(s))
    print(timedelta_hours(-2))


if __name__ == '__main__':
    test()
