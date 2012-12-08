# Create your views here.
from django.contrib.auth.decorators import login_required
from django.utils import simplejson
from django.http import HttpResponse

from annoying.decorators import render_to

from skaa.account_settings_views import settings_user
from doctor.account_settings_views import settings_doc

from common.functions import get_profile_or_None

import ipdb

import settings
import balanced

@login_required
def account_settings(request):
    # if user, send them to settings_user
    # if doc, send them to settings_doc
    profile = get_profile_or_None(request)
    if not profile:
        return redirect('/')

    if profile.is_doctor:
        return settings_doc(request)
    else:
        return settings_user(request)

    return {}

@login_required
def account_settings_delete_card(request):
    """
    Asynchronous call done to delete the card associated with request.POST['card_uri']
    """
    card_uri = request.POST['card_uri']
    # Now, it would take some mighty fine guessing to predict a card uri, but we
    # gotta make sure that this card belongs to this user
    
    profile = get_profile_or_None(request)
    balanced.configure(settings.BALANCED_API_KEY_SECRET)
    acct = balanced.Account.find( profile.bp_account_wrapper.uri )
    user_card_uris = [ c.uri for c in acct.cards ]

    if card_uri in user_card_uris:
        card = balanced.Card.find( card_uri )
        card.is_valid = False
        card.save()
        result = { "success" : True }
    else:
        result = { "success" : False }

    response_data = simplejson.dumps(result)
    return HttpResponse(response_data, mimetype='application/json')

