# -*- coding: utf-8 -*-
"""
Custom template filters and tags used by the spray indicators.
"""
from django import template

from dateutil import parser

register = template.Library()  # pylint: disable=invalid-name

GREEN = "green"
ORANGE = "orange"
RED = "red"
YELLOW = "yellow"
NO_DECISION_FORM = "No decision form"


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

    color = GREEN

    if 75 < value < 90:
        color = ORANGE
    elif 20 < value <= 75:
        color = RED
    elif value <= 20:
        color = YELLOW

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


@register.filter
def structures_mopup_colour(value):
    """Returns a colour string dependent on structures remaining to reach 90%.

    green - when value is fewer than 10
    orange - when value is between 10 and 20
    red - when value is greater than 20
    no colour otherwise i.e empty string.
    """
    try:
        if value < 10:
            return GREEN

        if value in range(10, 20):
            return ORANGE

        if value > 20:
            return RED
    except TypeError:
        # ignore if we got a string instead
        pass

    return ""


@register.filter
def decision_date(value, arg):
    """Return the decision date if arg is within 2 days of the value."""
    if value and arg:
        the_date = parser.parse(value).date()
        days = (the_date - arg).days

        if days in range(0, 3):
            return value

    return NO_DECISION_FORM


@register.filter
def decision_date_colour(value, arg):
    """Return RED if arg is within 2 days of the value."""
    if decision_date(value, arg) == NO_DECISION_FORM:
        return RED

    return ""
