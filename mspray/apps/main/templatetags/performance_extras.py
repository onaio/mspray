from datetime import datetime
from django import template

register = template.Library()


@register.filter
def sprayed_color(value):
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
    if not isinstance(value, tuple):
        return value

    hour, minute = value

    return '{}:{}'.format('' if hour is None else hour,
                          '' if minute is None else minute)


@register.filter
def avg_start_time_color(value):
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
    if (not isinstance(value, tuple) or value is None) or \
            (not isinstance(from_value, tuple) or from_value is None):
        return ''
    start_time = '{}:{}'.format(*from_value)
    end_time = '{}:{}'.format(*value)

    if 'None' in start_time or 'None' in end_time:
        return ''

    start_time = datetime.strptime(start_time, '%H:%M')
    end_time = datetime.strptime(end_time, '%H:%M')
    time_diff = end_time - start_time

    minutes, seconds = divmod(time_diff.seconds, 60)
    hours, minutes = divmod(minutes, 60)

    return '%d:%02d' % (hours, minutes)


@register.simple_tag
def percentage(numerator, denominator):
    denominator = float(denominator)
    numerator = float(numerator)
    if denominator == 0:
        return ''

    return '%d%%' % round((numerator * 100) / denominator)
