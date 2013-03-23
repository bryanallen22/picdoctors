# Create your views here.
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate
from django.utils import simplejson
from django.http import HttpResponse
from django.core.urlresolvers import reverse

from annoying.decorators import render_to

from skaa.account_settings_views import get_settings_user
from doctor.account_settings_views import get_settings_doc

from common.functions import get_profile_or_None
from common.balancedfunctions import get_merchant_account


import logging

import settings
import balanced
import ipdb

@login_required
def get_shared_params(request, profile):

    return {
        'email'           : request.user.email,
        'marketplace_uri' : settings.BALANCED_MARKETPLACE_URI,
    }

@login_required
@render_to('account_settings.html')
def account_settings(request):
    # if user, send them to settings_user
    # if doc, send them to settings_doc
    profile = get_profile_or_None(request)
    if not profile:
        return redirect('/')

    # Okay, Bryan is a bad person. This is a horrible hack upon hacks, and
    # all of this stuff needs a rewrite. Eventually. So.
    # This method is the handles user settings for both doctors and users.
    # They have a shared parent template, and we need to fetch some basics
    # for the parent template. Child handlers fetch things for the child
    # template things.

    parent_params = get_shared_params(request, profile)
    
    if profile.isa('doctor'):
        child_params = get_settings_doc(request)
        parent_params.update(child_params)
    
    if profile.isa('skaa'):
        child_params = get_settings_user(request)
        parent_params.update(child_params)

    return parent_params


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
    acct = profile.bp_account.fetch()
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

@login_required
def change_password(request):
    # Send them back to their current page

    profile = get_profile_or_None(request)
    user = authenticate(username=request.user.email,
                        password=request.POST['old_password'])

    if user and user.is_active and user == request.user:
        if request.POST['new_password'] == request.POST['confirm_password']:
            user.set_password( request.POST['new_password'] )
            user.save()
            result = { 'success' : True }
        else:
            result = { 'nomatch' : True }
    else:
        result = { 'bad_oldpassword' : True }

    response_data = simplejson.dumps(result)
    return HttpResponse(response_data, mimetype='application/json')

@login_required
def change_email(request):

    profile = get_profile_or_None(request)
    new_email = request.POST['new_email']
    old_email = request.user.email

    # Initialize to fail
    result = { 'success' : False }

    logging.info("Changing user email %s to %s" % (request.user.email, new_email))

    # Change the email on the balanced side
    try:
        account = get_merchant_account(request, profile)
        account.email_address = new_email
        account.save()

        request.user.email = new_email
        request.user.save()

        result = { 'success' : True }
    except:
        # TODO - make sure our local db copy is okay
        logging.info("Error updating user email from %s to %s! Resetting our local copy, just in case."
                     % (request.user.email, new_email))
        request.user.email = old_email
        request.user.save()
        raise
    
    response_data = simplejson.dumps(result)
    return HttpResponse(response_data, mimetype='application/json')

@login_required
def update_roles(request):
    profile = get_profile_or_None(request)
    success = False
    redirect = ''

    prole = request.POST['role']
    role = '' # hah, no way we set whatever role they want here

    if prole == 'doctorswitch':
        role = 'doctor'
    elif prole == 'userswitch':
        role = 'skaa'
    elif prole == 'approvalswitch' and not settings.IS_PRODUCTION:
        role = 'approve_album'
    else:
        return # break on them, I don't care

    state = request.POST['state'] == 'true'
    
    if profile:
        if state:
            profile.add_permission(role)
        else:
            profile.remove_permission(role)
        
        success = True
        redirect =  reverse('account_settings') + '#roles_tab' 

    ret = { 
            "success" : True,
            "redirect"  : redirect,
            }

    response_data = simplejson.dumps(ret)
    return HttpResponse(response_data, mimetype='application/json')
