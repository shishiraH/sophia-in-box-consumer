from datetime import datetime, date, timedelta
import time


def get_limit_timetamp():
    pattern = '%d-%m-%Y 00:00:00'
    yesterday = (date.today() - timedelta(days=1)).strftime(pattern)
    today = date.today().strftime(pattern)

    yesterday_epoch = int(time.mktime(time.strptime(yesterday, pattern))) * 1000
    today_epoch = int(time.mktime(time.strptime(today, pattern))) * 1000
    return yesterday_epoch, today_epoch


def get_readable_date(timestamp):
    date_obj_str = datetime.fromtimestamp(timestamp / 1000).strftime('%Y-%m-%d %H:%M:%S')
    return date_obj_str


def get_today_string():
    return date.today().strftime('%d-%b-%Y')
