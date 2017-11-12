# -*- coding=utf-8 -*-
"""
Custom performance template tags and filters.
"""
from datetime import datetime, time, timedelta
from django import template

register = template.Library()


@register.filter
def sprayed_color(value):
    """
    Returns 'green' or 'red' or 'yellow' string depending on value.
    """
    try:
        if not isinstance(value, (int, float, complex)):
            value = float(value)
    except ValueError:
        return ''

    color = 'green'

    if value < 12:
        color = 'red'
    elif value >= 12 and value < 14:
        color = 'yellow'

    return color


@register.filter
def format_avg_time(value):
    """
    Formats a (hour, minute) tuple to 'hour:minute' string.
    """
    if not isinstance(value, tuple):
        return value if value is not None else ''

    hour, minute = value

    if hour is None or minute is None:
        return ''

    return '{:02}:{:02}'.format(hour, minute)


@register.filter
def avg_start_time_color(value):
    """
    Returns 'red' or 'green' or 'yellow' string depending on the start hour.
    """
    if not isinstance(value, tuple) or value is None:
        return ''

    color = 'red'
    hour, minute = value
    if hour is None or minute is None:
        color = ''
    elif hour < 8:
        color = 'green'
    elif hour == 8 and minute >= 0 and minute <= 30:
        color = 'yellow'

    return color


@register.filter
def avg_end_time_color(value):
    """
    Returns 'red' or 'green' or 'yellow' string depending on the end hour.
    """
    if not isinstance(value, tuple) or value is None:
        return ''

    color = 'red'
    hour, minute = value

    if hour is None or minute is None:
        color = ''
    elif hour >= 15:
        color = 'green'
    elif hour >= 14 and hour < 15:
        color = 'yellow'

    return color


@register.simple_tag
def avg_time_interval(value, from_value):
    """
    Returns the time differennce between value - from_value.
    """
    value_is_time = isinstance(value, time)
    from_value_is_time = isinstance(value, time)
    values_are_none = value is None or from_value is None
    if ((not isinstance(value, tuple) and not value_is_time) or
            values_are_none or (not isinstance(from_value, tuple) and
                                not from_value_is_time)):
        return ''
    if value_is_time and from_value_is_time:
        start_time, end_time = from_value, value
        return '%s' % (
            timedelta(hours=end_time.hour, minutes=end_time.minute,
                      seconds=end_time.second) - timedelta(
                          hours=start_time.hour, minutes=start_time.minute,
                          seconds=start_time.second)
        )

    start_time = '{}:{}'.format(*from_value)
    end_time = '{}:{}'.format(*value)

    if 'None' in start_time or 'None' in end_time:
        return ''

    start_time = datetime.strptime(start_time, '%H:%M')
    end_time = datetime.strptime(end_time, '%H:%M')
    time_diff = end_time - start_time

    minutes, _seconds = divmod(time_diff.seconds, 60)
    hours, minutes = divmod(minutes, 60)

    return '{:02}:{:02}'.format(hours, minutes)


@register.simple_tag
def percentage(numerator, denominator):
    """
    Returns percentage formatted string from numerator/denominator.
    """
    try:
        denominator = float(denominator)
        numerator = float(numerator)
    except ValueError:
        return ''

    if denominator == 0:
        return ''

    return '{:.0%}'.format(numerator / denominator)
