# Create your views here.
from django.contrib.auth.decorators import login_required

from annoying.decorators import render_to
from common.functions import get_profile_or_None

import settings

import ipdb

@login_required
@render_to('account_settings_user.html')
def settings_user(request, parent_params):
    profile = get_profile_or_None(request)
    
    if profile.bp_account_wrapper:
        acct = profile.bp_account_wrapper.fetch()

        user_credit_cards = [c for c in acct.cards if c.is_valid]
    else:
        user_credit_cards = []

    my_params = {
        'credit_cards':     user_credit_cards,
    }

    my_params.update(parent_params)

    return my_params

