# Create your views here.
from django.contrib.auth.decorators import login_required

from annoying.decorators import render_to
from common.functions import get_profile_or_None

import balanced
import settings

import ipdb

@login_required
@render_to('account_settings_user.html')
def settings_user(request):
    email_address = request.user.email
    profile = get_profile_or_None(request)
    
    balanced.configure(settings.BALANCED_API_KEY_SECRET)

    if profile.bp_account_wrapper:
        # Get the balanced account info. This is slow.
        acct = balanced.Account.find( profile.bp_account_wrapper.uri )

        user_credit_cards = [c for c in acct.cards if c.is_valid]
    else:
        user_credit_cards = []

    return {
        'email':            email_address,
        'credit_cards':     user_credit_cards,
    }
