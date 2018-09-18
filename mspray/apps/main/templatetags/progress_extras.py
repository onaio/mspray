# -*- coding: utf-8 -*-
"""
Custom template filters and tags used by the spray indicators.
"""
from django import template

register = template.Library()  # pylint: disable=invalid-name


@register.filter
def sprayed_effectively_color(value):
    """
    Returns the text color for a given sprayed effectively percentage value. It
    will return:
        - green: when sprayed_effectively percentage is >= 90%.
        - orange: when sprayed_effectively percentage is between 75% and 90%
        - red: when sprayed_effectively percentage is between 20% and 75%
        - yellow: when sprayed_effectively percentage is less than 20%
    """
    # ignore last character because it's a percentage
    if isinstance(value, str):
        value = value[:-1]
    try:
        if not isinstance(value, (int, float, complex)):
            value = float(value)
    except ValueError:
        return ""

    color = "green"

    if 75 < value < 90:
        color = "orange"
    elif 20 < value <= 75:
        color = "red"
    elif value <= 20:
        color = "yellow"

    return color


@register.simple_tag
def calc_percentage(numerator, denominator):
    """
    Returns calculated percentage given a numerator and a denominator as
    arguments upto one decimal place. Otherwise, returns an empty string if the
    denominator is zero or a ValueError exception occured.
    """
    try:
        denominator = float(denominator)
        numerator = float(numerator)
    except ValueError:
        return ""

    if denominator == 0:
        return ""

    return "{:.0%}".format(numerator / denominator)


@register.filter
def key(data, key_name):
    """
    Returns the value in the given key_name of a dict.
    """
    return data.get(key_name)
