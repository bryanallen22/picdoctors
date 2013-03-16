# Create your views here.
from django.contrib.auth.decorators import login_required

from annoying.decorators import render_to
from common.functions import get_profile_or_None
from django.core.urlresolvers import reverse
from django.utils import simplejson
from django.http import HttpResponse

import settings

import ipdb

def get_settings_user(request):
    profile = get_profile_or_None(request)
    
    if profile.bp_account:
        acct = profile.bp_account.fetch()

        user_credit_cards = [c for c in acct.cards if c.is_valid]
    else:
        user_credit_cards = []

    my_params = {
        'credit_cards':     user_credit_cards,
    }

    return my_params

