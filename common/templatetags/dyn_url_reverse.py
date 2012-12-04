from django import template
from django.core.urlresolvers import reverse

register = template.Library()

@register.filter
def dyn_url_reverse(val, arg):
    """allows dynamic template tags to be reversed (single arg)"""
    return reverse(val, args=[arg])
