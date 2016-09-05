from django import template

register = template.Library()


@register.filter
def sprayed_effectively_color(value):
    # ignore last character because it's a percentage
    if isinstance(value, str):
        value = value[:-1]
    try:
        if not isinstance(value, (int, float, complex)):
            value = float(value)
    except ValueError:
        return ''

    color = 'green'

    if 75 < value <= 85:
        color = 'orange'
    elif 20 < value <= 75:
        color = 'red'
    elif value <= 20:
        color = 'yellow'

    return color


@register.assignment_tag
def calc_percentage(numerator, denominator):
    try:
        denominator = float(denominator)
        numerator = float(numerator)
    except ValueError:
        return ''

    if denominator == 0:
        return ''

    return '{:.0%}'.format(numerator / denominator)