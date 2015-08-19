from django import template

register = template.Library()


@register.filter
def sprayed_color(value):
    color = 'green'

    if value < 12:
        color = 'red'
    elif value >= 12 and value <= 14:
        color = 'yellow'

    return color
