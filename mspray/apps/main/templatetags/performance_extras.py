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
    elif value >= 12 and value <= 14:
        color = 'yellow'

    return color


@register.filter
def format_avg_time(value):
    if not isinstance(value, tuple):
        return value
    return '%s:%s' % value


@register.filter
def avg_start_time_color(value):
    if not isinstance(value, tuple):
        return ''

    color = 'green'
    hour, minute = value

    if hour > 8 and minute > 30:
        color = 'red'
    elif hour >= 8 and minute >= 0 and minute <= 30:
        color = 'yellow'

    return color


@register.filter
def avg_end_time_color(value):
    if not isinstance(value, tuple):
        return ''

    color = 'green'
    hour, minute = value

    if hour > 8 and minute > 30:
        color = 'red'
    elif hour >= 8 and minute >= 0 and minute <= 30:
        color = 'yellow'

    return color
