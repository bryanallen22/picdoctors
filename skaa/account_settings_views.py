# Create your views here.

from annoying.decorators import render_to
from common.functions import get_profile_or_None
from django.core.urlresolvers import reverse
from django.utils import simplejson
from django.http import HttpResponse
from common.stripefunctions import stripe_get_credit_cards

import settings

import ipdb

def get_settings_user(request):
    profile = get_profile_or_None(request)

    user_credit_cards = stripe_get_credit_cards(profile)

    my_params = {
        'credit_cards':     user_credit_cards,
    }

    return my_params

