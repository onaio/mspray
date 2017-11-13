# -*- coding=utf-8 -*-
"""
average_time util function
"""
from datetime import datetime, timedelta


def average_time(times):
    """
    Average time from a list of times.
    """
    count = len(times)
    if not count:
        return ''
    seconds = sum([
        timedelta(hours=x.hour, minutes=x.minute, seconds=x.second).seconds
        for x in times
    ])
    avg = timedelta(seconds=(seconds / round(count)))

    time_format_str = '%H:%M:%S.%f' if avg.microseconds != 0 else '%H:%M:%S'

    return datetime.strptime('%s' % avg, time_format_str).time()
