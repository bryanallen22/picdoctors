# Create your views here.
from django.contrib.auth import authenticate
from django.utils import simplejson
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.shortcuts import redirect

from annoying.decorators import render_to

from skaa.account_settings_views import get_settings_user
from doctor.account_settings_views import get_settings_doc

from common.functions import get_profile_or_None
from common.balancedfunctions import get_merchant_account
from notifications.models import Notification, NotificationToIgnore
from common.decorators import require_login_as
from common.models import Profile, Pic
import re

import logging

import settings
import balanced
import ipdb

class NotificationInfo:
    def __init__(self):
        self.type = 'moo'
        self.description = 'cow'
        self.enabled = False

def get_shared_params(request, profile):

    return {
        'marketplace_uri' : settings.BALANCED_MARKETPLACE_URI,
    }

@require_login_as(['skaa', 'doctor'])
@render_to('account_settings.html')
def account_settings(request):
    profile = get_profile_or_None(request)

    if request.method == 'POST':
        file = request.FILES[u'file'] if 'file' in request.FILES else None
        if file is not None:
            pic = Pic(path_owner="doc_profile")
            pic.set_file(file, thumb_width=200,   thumb_height=200,
                               preview_width=200, preview_height=200);
            pic.save()
            request.user.pic = pic
            request.user.save()
        if 'doc_profile_desc' in request.POST:
            request.user.doc_profile_desc = request.POST['doc_profile_desc']
            request.user.save()

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

    notification_json = get_notification_list(profile)
    parent_params['notification_json'] = notification_json

    return parent_params

def get_notification_list(profile):
    nts = []
    ignore_list = NotificationToIgnore.objects.filter(profile=profile).filter(ignore=True)
    for tup in Notification.NOTIFICATION_TYPES:
        if tup[0]==Notification.JOBS_AVAILABLE and not profile.isa('doctor'):
            continue

        if tup[0]==Notification.JOBS_NEED_APPROVAL and not profile.has_perm('common.album_approver'):
            continue
            
        enabled = len([s for s in ignore_list if s.notification_type == tup[0]]) == 0
        n = NotificationInfo()
        n.type = tup[0]
        n.description = tup[1]
        n.enabled = enabled
        
        nts.append(n.__dict__)

    return simplejson.dumps(nts)


@require_login_as(['skaa'])
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

@require_login_as(['skaa', 'doctor'])
def change_password(request):
    # Send them back to their current page

    profile = get_profile_or_None(request)
    user = authenticate(username=request.user.email,
                        password=request.POST['old_password'])

    if user and user.is_active and user == request.user:
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']
        if not legit_password(new_password):
            result = { 'invalid_pass': True }
        elif new_password == confirm_password:
            user.set_password( request.POST['new_password'] )
            user.save()
            result = { 'success' : True }
        else:
            result = { 'nomatch' : True }
    else:
        result = { 'bad_oldpassword' : True }

    response_data = simplejson.dumps(result)
    return HttpResponse(response_data, mimetype='application/json')

def legit_password(password):
    if settings.IS_PRODUCTION:
        if len(password) > 7:
            return True
    else: # for non production we need at least 1 character
        if len(password) > 0:
            return True
    return False



@require_login_as(['skaa', 'doctor'])
def change_profile_settings(request):
    profile = get_profile_or_None(request)
    nickname = request.POST['nickname']
    new_email = request.POST['email']
    old_email = request.user.email

    # Initialize to fail
    result = { 'success' : False, 'text': 'Oh no, something bad has happened!' }

    logging.info("Changing user email %s to %s" % (request.user.email, new_email))

    # Change the email on the balanced side
    try:
        account = get_merchant_account(request, profile)
        account.email_address = new_email
        account.save()

        request.user.email = new_email
        request.user.nickname = nickname
        request.user.save()

        result = { 'success' : True , 'text': 'We successfully updated your account settings!'}
    except:
        # TODO - make sure our local db copy is okay
        logging.info("Error updating user email from %s to %s! Resetting our local copy, just in case."
                     % (request.user.email, new_email))
        request.user.email = old_email
        request.user.save()
        raise
    
    response_data = simplejson.dumps(result)
    return HttpResponse(response_data, mimetype='application/json')

@require_login_as(['skaa', 'doctor'])
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
        role = 'album_approver'
    elif prole == 'admin' and not settings.IS_PRODUCTION:
        role = 'admin'
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
