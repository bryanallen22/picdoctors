# Create your views here.
from django.contrib.auth.decorators import login_required

from annoying.decorators import render_to
from common.functions import get_profile_or_None
from django.core.urlresolvers import reverse
from django.utils import simplejson
from django.http import HttpResponse

import settings

import ipdb

def get_settings_user(request, parent_params):
    profile = get_profile_or_None(request)
    
    if profile.bp_account:
        acct = profile.bp_account.fetch()

        user_credit_cards = [c for c in acct.cards if c.is_valid]
    else:
        user_credit_cards = []

    my_params = {
        'credit_cards':     user_credit_cards,
    }

    my_params.update(parent_params)

    return my_params

@login_required
def become_a_pic_doctor(request):
    profile = get_profile_or_None(request)
    success = False
    redirect = ''
    if profile:
        if not profile.isa('doctor'):
            profile.add_permission('doctor')
            success = True
            redirect =  reverse('account_settings') + '#merchant_tab' 

    ret = { 
            "success" : True,
            "redirect"  : redirect,
            }

    response_data = simplejson.dumps(ret)
    return HttpResponse(response_data, mimetype='application/json')
