import datetime
import time


def get_timestamp_in_milli(_datetime=None):
    """
    returns timestamp in millisecond
    """
    now = datetime.datetime.now()
    if _datetime:
        now = _datetime
        if isinstance(_datetime, datetime.date):
            now = datetime.datetime.combine(_datetime, datetime.time.min)
    result = int(time.mktime(now.timetuple())*1000 + now.microsecond/1000)
    return result


def get_datetime_from_timestamp(timestamp):
    return datetime.datetime.fromtimestamp(timestamp/1000.0)


def get_age_from_timestamp(timestamp_ms):
    timestamp_sec = timestamp_ms / 1000 
    born = datetime.datetime.fromtimestamp(timestamp_sec).date()
    today = datetime.date.today() 
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))


def get_days_from_timestamp(timestamp_ms):
    days_ms = get_timestamp_in_milli() - timestamp_ms
    return (days_ms + 1000 * 60 * 60 * 24 - 1) / (1000 * 60 * 60 * 24)
