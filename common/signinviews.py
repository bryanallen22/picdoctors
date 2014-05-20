from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.utils import simplejson

from annoying.decorators import render_to
from annoying.functions import get_object_or_None

from common.functions import json_result
from common.functions import get_profile_or_None

from common.models import Album, Profile
from common.account_settings_views import legit_password
from doctor.jobsviews import doc_job_page
from skaa.progressbarviews import get_progressbar_vars, show_progressbar_on_login_page
from views import index
from emailer.emailfunctions import send_email
import string
import re

import ipdb
import logging; log = logging.getLogger('pd')
import datetime
import settings

def create_skaa(request, user):
    user.add_permission('skaa')
    from emailer.emailfunctions import DEFAULT_CONTACT_EMAIL
    send_email( request=request,
                email_address=user.email,
                template_name='skaa_signup.html',
                template_args={
                    'profile' : user,
                    'contact_email' : DEFAULT_CONTACT_EMAIL,
                }
              )

def create_doctor(request, user):
    user.add_permission('doctor')
    from emailer.emailfunctions import DEFAULT_CONTACT_EMAIL
    send_email( request=request,
                email_address=user.email,
                template_name='doc_signup.html',
                template_args={
                    'profile' : user,
                    'contact_email' : DEFAULT_CONTACT_EMAIL,
                }
              )

def auth(email, password):
    """
    Authenticate the user.

    Possible return values:
        { } -- Everything good
        { 'bad_email_or_password' : True } -- Self explanatory
    """
    email = email.lower()
    user = authenticate(username=email, password=password)
    if user is not None and user.is_active:
        return ( user, { } )
    return ( None, { 'bad_email_or_password' : True } )

def create_user(request, email, nickname, password, confirm_password, usertype):
    """
    Create the user.

    usertype should be:
        'user' -- create a skaa
        'doc'  -- create a doctor

    If the email is taken and the password matches that
    email, just be nice and log them in.

    Possible return values:
      ( user, { } )
          Everything good
      ( None, { 'email_already_exists'  : True } )
          Email address taken, and password didn't match
      ( None, { 'passwords_didnt_match' : True } )
          Self explanatory
    """

    # you shouldn't be able to create two different users with different emails
    # just based on capitalization
    email = email.lower()
    email_reg = re.compile('.+\@.+\..+')
    match = email_reg.match(email)

    # This just verifies a@a.a
    if not match:
        return ( None, { 'bad_email_or_password' : True } )

    # make sure the nickname only has a-zA-Z0-9
    valid_chars = "_%s%s" % (string.ascii_letters, string.digits)
    new_nickname = ''.join(c for c in nickname if c in valid_chars)

    if new_nickname != nickname:
        return ( None, { 'invalid_nick' : True } )

    if Profile.objects.filter(nickname=nickname).count() > 0:
        return ( None, { 'invalid_nick' : True } )

    if password != confirm_password:
        return ( None, { 'passwords_didnt_match' : True } )

    if not legit_password(password):
        return ( None, { 'password_invalid' : True } )


    if Profile.objects.filter(email=email).count() > 0:
        # Username exists... Can we log in?
        user, tmp = auth(email, password)
        if not user:
            # Error with those credentials
            return ( None, { 'email_already_exists' : True } )
        else:
            # We signed them in just fine
            return ( user, { } )
    else:
        user = Profile.objects.create_user(email=email, password=password)
        #Now authenticate the user (it puts the backend into the User object)
        user, tmp = auth(email, password)
        # The Profile for this person has already been automatically created
        # based on the post_save signal tied to the User class. See create_user_profile
        # in common/models.py
        user.nickname = nickname
        user.save()

        if usertype == 'doc':
            create_doctor(request, user)
        elif usertype == 'user':
            create_skaa(request, user)
        else:
            raise ValueError('Bad usertype: %s' % usertype)

        return ( user, { } )

@render_to('signin.html')
def signin(request, usertype='user'):
    """
    Shared view for both user login and doctor login

    usertype should be 'user' or 'doc'
    """
    # if you're already logged in you shouldn't be here
    profile = get_profile_or_None(request)
    if profile and ( profile.isa('doctor') or profile.isa('skaa') ):
        if 'next' in request.GET:
            return redirect( request.GET['next'] )
        else:
            return redirect('/')

    # Set defaults here. Overridden below if necessary
    ret = { 'usertype' : usertype , 'create_checked' : 'checked'}

    if request.method == 'GET':
        # if they aren't going anywhere, they clicked login, show login by default, not create
        if not 'next' in request.GET:
            ret['have_checked'] = 'checked'
            ret['create_checked'] = ''
        # Nothing to do here now...
        pass

    elif request.method == 'POST':
        # Do they have a album in the session? If so, let's keep a handle on it
        # so we can associate it with the user's profile.
        album = Album.get_unfinished(request)

        # Sign into existing account
        if request.POST['create_acct_radio'] == 'have':
            user, tmp = auth( request.POST['email'], request.POST['password'] )
            ret.update(tmp)

        # Create a new account
        else:

            if 'agree_tos' not in request.POST.keys():
                user, tmp = ( None, { 'need_tos' : True } )
            else:
                user, tmp = create_user( request,
                                         request.POST['email'],
                                         request.POST['nickname'],
                                         request.POST['password'],
                                         request.POST['confirm_password'],
                                         usertype )
            ret.update(tmp)

        if user:
            # Successful login. Take care of "remember me" button
            login(request, user)

            associate_album(request, album, user)

            if 'remember' in request.POST.keys():
                # "Remember Me" is good for 30 days
                one_month = datetime.timedelta(days=30)
                request.session.set_expiry( one_month )
            else:
                # Session only good until browser closes
                request.session.set_expiry(0)

            if 'next' in request.GET:
                return redirect( request.GET['next'] )
            else:
                # No idea where to send them. Send them to the home page.
                return redirect( '/' )

        else:
            # Something went wrong. Let's at least prepopulate the email address for them
            ret['email'] = request.POST['email']
            ret['nickname'] = request.POST['nickname']
            if request.POST['create_acct_radio'] == 'have':
                ret['have_checked'] = 'checked'
            elif request.POST['create_acct_radio'] == 'create':
                ret['create_checked'] = 'checked'

    # Do
    if usertype == 'user' and show_progressbar_on_login_page(request):
        ret['show_progressbar'] = True
        ret.update( get_progressbar_vars(request, 'signin') )
    else:
        ret['show_progressbar'] = False
    return ret

#Nothing special here, we don't need to check if they are logged in or not#I'm just lazy and want to sign out, logic of this needs to be looked at
def signout(request):
    logout(request)
    return redirect('/')

def associate_album(request, album, user):
    if album is not None:
        album.userprofile = user
        album.save()

    # Once it has a user, clear the session back out
    Album.clear_session_album(request)

def skaa_signin(request):
    # Don't use the word 'skaa' here -- it'll be visible in the html : )
    return signin(request, usertype='user')

def doc_signin(request):

    return signin(request, usertype='doc')


def valid_nick(nickname):
    if nickname.strip() == "":
        result = {
            'success'   : False,
            'text'      : "You're nickname can't be blank",
            }
    elif len(nickname) > 32:
        result = {
            'success'   : False,
            'text'      : "You're nickname can't be greater then 32 characters long",
            }
    elif not re.match('^[a-zA-Z0-9_]+$', nickname):
        result = {
            'success'   : False,
            'text'      : "You're nickname can only contain letters, numbers and underscores",
            }
    else:
        result= {'success':True}

    return result


#@require_login_as([])
# no required login
def check_unique_nickname(request):
    try:
        nickname = request.POST['nickname']
        result = valid_nick(nickname)
        if result.get('success'):
            nick_count = Profile.objects.filter(nickname=nickname).count()
            if nick_count == 0:

                result = {
                       'success' : True,
                       'text'    : 'That nickname is available!',
                         }
            else:
                result = {
                        'success' :False,
                        'text' : "That nickname is already in use!",
                        }
    except:
        result = {
                'success' : False,
                'text' : "There was an unexpected error, we may be unable to save your nickname"
                 }

    response_data = simplejson.dumps(result)
    return HttpResponse(response_data, mimetype='application/json')

