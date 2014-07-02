from annoying.decorators import render_to
from django.http import HttpResponse

from django.utils import simplejson

from common.functions import json_result
from skaa.markupviews import can_modify_markup
from annoying.functions import get_object_or_None

from common.decorators import require_login_as
from notifications.models import NotificationToIgnore

import ipdb

@render_to('home.html')
def home(request):
    return {}

def users_endpoint(request, user_id):
    profile = request.user

    if not profile.is_authenticated():
        return unauthenticated_user()

    user = {}
    user['id'] = profile.id
    user['nickname'] = profile.nickname
    user['email'] = profile.email
    user['isLoggedIn'] = True
    user['emailConfig'] = profile.id # He uses the profile id as a key to get the notifications to ignore

    roles = get_roles(profile)
    user['roles'] =  [r['id'] for r in roles]

    return json_result({
        "user":user,
        "roles": roles
        })

def unauthenticated_user():
    user = {
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
    types=NotificationToIgnore.objects.filter(profile=request.user).filter(ignore=True)

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
    return len([t for t in types if t.notification_type == type]) == 0

def remove_role(request, role_id):
    user = request.user
    role_id = int(role_id)

    if not user.is_authenticated():
        raise

    permissions = user.user_permissions.all()
    role = next((r for r in permissions if r.id == role_id), None)

    if role:
        user.user_permissions.remove(role)
        return HttpResponse(status=204)

    ret = simplejson.dumps({'error':'failure'})
    return HttpResponse(ret, status=500, mimetype='application/json')

