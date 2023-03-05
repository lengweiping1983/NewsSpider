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
            maybe_date = datetime.datetime.strptime(str(today.year) + '-' + match.group(), '%Y-%m-%d %H:%M')
            if maybe_date > today:
                return datetime.datetime.strptime(str(today.year - 1) + '-' + match.group(), '%Y-%m-%d %H:%M')
            return maybe_date
        match = re.search(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}', source)
        if match is not None:
            return datetime.datetime.strptime(match.group(), '%Y-%m-%dT%H:%M:%S')
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


def timedelta_minutes(minutes):
    return datetime.datetime.now() + datetime.timedelta(minutes=minutes)


def test():
    s = "Jason's birthday is on 1991-09-21 18:22:21"
    s = "Jason's birthday is on 1991-09-21 18:22"
    s = "Jason's birthday is on 02-21 18:22"
    # s = "Jason's birthday is on 2023-03-04T22:38:03.004Z"
    # s = "Jason's birthday is on 1991-09-21"
    # print(parse_str_get_date(s))
    # print(timedelta_minutes(-2))
    pass


if __name__ == '__main__':
    test()
