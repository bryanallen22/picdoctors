from django import template
from django.core.urlresolvers import reverse
import locale

register = template.Library()
locale.setlocale(locale.LC_ALL, '')

@register.filter
def dyn_url_reverse(val, arg):
    """allows dynamic template tags to be reversed (single arg)"""
    return reverse(val, args=[arg])

@register.filter
def currency(value):
    """ format as currency """

    # Someday, when we move to python 3.x, change this to isinstance(value, str)
    if isinstance(value, basestring):
        value = float(value)
    return locale.currency(value, grouping=True)

