from annoying.decorators import render_to
from django.contrib.auth import authenticate
from django.http import HttpResponse

from django.utils import simplejson

from common.functions import json_result
from skaa.markupviews import can_modify_markup
from annoying.functions import get_object_or_None

from common.decorators import require_login_as
from notifications.models import NotificationToIgnore
from common.stripefunctions import *
from common.models import Profile
import re

import ipdb

@render_to('home.html')
def home(request):
    return {}

def users_endpoint(request, user_id):
    profile = request.user
    response = {}
    if not profile.is_authenticated():
        return unauthenticated_user()

    if request.method == 'GET':
        response = fetch_user(profile)
    elif request.method == 'PUT':
        data = simplejson.load(request)['user']
        response = save_user(profile, data)


    return json_result(response)

def fetch_user(profile):
    user = {}
    user['id'] = profile.id
    user['nickname'] = profile.nickname
    user['email'] = profile.email
    user['stripe_user'] = profile.stripe_connect.stripe_user_id if profile.stripe_connect else None
    user['isLoggedIn'] = True
    user['emailConfig'] = profile.id # He uses the profile id as a key to get the notifications to ignore

    roles = get_roles(profile)
    user['roles'] =  [r['id'] for r in roles]

    return {
        "user":user,
        "roles": roles
        }

def save_user(profile, data):
    email = data['email'].lower()
    email_reg = re.compile('.+\@.+\..+')
    match = email_reg.match(email)

    # you couldn't have hit this endpoint with an invalid email
    # unless you are manually posting to it... uh oh
    if not match:
        raise
    
    # I should do this nicer, but I'm not going to now
    if Profile.objects.filter(email=email).exclude(id=profile.id).count() > 0:
        raise

    profile.email = email
    # TODO Email the user when they change their password!
    profile.save()
    # I'm intentionally not returning anything, sending back nothing is just as cool
    # as sending back something, in fact it's easier

def unauthenticated_user():
    user  = {
            'id': -1,
            'nickname': 'visitor',
            'email': 'email',
            'isLoggedIn': False,
            'roles': [-1]
           }

    return json_result({
        "user":user,
        "roles": [
            {
                "id" : -1,
                "name": "user",
                "user": "-1"
            }
            ]
        })

clean_roles = {
  "skaa" : "user"
}

def clean_role(role):
    inRoles = role in clean_roles
    if inRoles:
        return clean_roles[role]
    else:
        return role

def get_roles(profile):
    ret = []
    permissions = profile.user_permissions.all()
    for perm in permissions:
        p = {
                'id': perm.id,
                'name': clean_role(perm.codename),
                'user': profile.id
            }
        ret.append(p)
    return ret



@require_login_as(['skaa', 'doctor'])
def email_config_endpoint(request, user_id):
    profile = request.user
    types=list(NotificationToIgnore.objects.filter(profile=request.user))

    if request.method == 'PUT':
        data = simplejson.load(request)['emailConfig']
        set_emails(types, data, profile)

    result = {
      'emailConfig' : {
      'id':                 request.user.id,
      'job_status_change':  wants_email(types, 'jb_status_chg'),
      'jobs_available':     wants_email(types, 'jb_ava'),
      'jobs_need_approval': wants_email(types, 'jb_need_app'),
      'job_reminder':       wants_email(types, 'jb_remind'),
      'job_message':        wants_email(types, 'jb_msg'),
      'job_rejection':      wants_email(types, 'jb_rejection'),
      'job_switched':       wants_email(types, 'jb_switched'),
       }
    }

    return json_result(result)

def wants_email(types, type):
    return len([t for t in types if t.notification_type == type and t.ignore == True]) == 0

def set_emails(types, json, profile):
    set_email(types, 'jb_status_chg', json['job_status_change'], profile)
    set_email(types, 'jb_ava', json['jobs_available'], profile)
    set_email(types, 'jb_need_app',json['jobs_need_approval'], profile)
    set_email(types, 'jb_remind', json['job_reminder'], profile)
    set_email(types, 'jb_msg', json['job_message'], profile)
    set_email(types, 'jb_rejection', json['job_rejection'], profile)
    set_email(types, 'jb_switched', json['job_switched'], profile)

def set_email(types, type, value, profile):
    records = [t for t in types if t.notification_type == type]

    wants_email = len(records) == 0 or records[0].ignore == False
    still_wants_email = value

    if wants_email != still_wants_email:
        if len(records) > 0:
            record = records[0]
            record.ignore = not record.ignore
            record.save()
        else:
            nti = NotificationToIgnore()
            nti.notification_type = type
            nti.profile = profile
            nti.ignore = not still_wants_email
            nti.save()
            types.append(nti)

def remove_role(request, role_id):
    profile = request.user
    role_id = int(role_id)

    if not profile.is_authenticated():
        raise

    permissions = profile.user_permissions.all()
    role = next((r for r in permissions if r.id == role_id), None)

    if role:
        profile.user_permissions.remove(role)
        return HttpResponse(status=204)

    ret = simplejson.dumps({'error':'failure'})
    return HttpResponse(ret, status=500, mimetype='application/json')

def add_role(request):
    user = request.user
    result = {}

    if not user.is_authenticated():
        raise

    if request.method == 'POST':
        data = simplejson.load(request)['role']
        name = data['name']
        p_name = name
        legal_roles = ['user', 'doctor']
        if not settings.IS_PRODUCTION:
            legal_roles.extend(('admin', 'album_approver'))

        if name == 'user':
            p_name = 'skaa'

        if name in legal_roles:
            perm = user.add_permission(p_name)
            result = {
              'role':{
                 'id':perm.id,
                 'name':name,
                 'doctor':user.id
              }
            }
        else:
            raise
    else:
        raise


    return json_result(result)

@require_login_as(['skaa'])
def creditcards(request, card_id=None):
    if request.method == 'GET':
        desired_attributes = ['id', 'brand', 'last4', 'exp_month', 'exp_year']
        stripe_cards = stripe_get_credit_cards(request.user)
        output_cards = []

        for stripe_card in stripe_cards:
            card = { }
            for attr in desired_attributes:
                card[attr] = stripe_card[attr]
            output_cards.append(card)

        result = {
            'creditcards' : output_cards
        }
        return json_result(result)
    elif request.method == 'DELETE':
        success = stripe_delete_credit_card(request.user, card_id)
        if success:
            return json_result( { } )
        else:
            return HttpResponse('Gone', status=403)

def hookup_stripe(request):
    user = request.user
    result = { 'success' : False}

    if not user.is_authenticated():
        raise

    if request.method == 'POST':
        code = request.POST['code']
        scope = request.POST['scope']
        if code:
            resp= get_stripe_access_token_response(code)
            json = resp.json()
            if json.get('access_token'):
                connect_stripe_connect_account(user, json)
                result = { 
                        'success' : True,
                        'stripe_user' : user.stripe_connect.stripe_user_id
                        }

    # create a kinder response
    if not result['success']:
        raise

    return json_result(result)

def change_password(request):
    profile = request.user
    # Send them back to their current page
    if not profile.is_authenticated():
        raise

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
