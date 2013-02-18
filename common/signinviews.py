from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError

from annoying.decorators import render_to
from annoying.functions import get_object_or_None

from common.models import Album, UserProfile, DoctorInfo, SkaaInfo
from doctor.jobsviews import doc_job_page
from views import index

import ipdb
import logging
import datetime

def create_skaa(user_profile):
    set_is_doctor(user_profile, False)
    SkaaInfo.objects.create(user_profile=user_profile)

def create_doctor(user_profile):
    set_is_doctor(user_profile, True)
    DoctorInfo.objects.create(user_profile=user_profile)

def set_is_doctor(user, val):
    user.is_doctor = val
    user.save()

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

def create_user(email, password, confirm_password, usertype):
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
    if password != confirm_password:
        return ( None, { 'passwords_didnt_match' : True } )

    if User.objects.filter(email=email).count() > 0:
        # Username exists... Can we log in?
        user, tmp = auth(email, password)
        if not user:
            # Error with those credentials
            return ( None, { 'email_already_exists' : True } )
        else:
            # We signed them in just fine
            return ( user, { } )
    else:
        user = User.objects.create_user(username=email, email=email, password=password)
        #Now authenticate the user (it puts the backend into the User object)
        user, tmp = auth(email, password)
        # The UserProfile for this person has already been automatically created
        # based on the post_save signal tied to the User class. See create_user_profile
        # in common/models.py
        user_profile = user.get_profile()
        if usertype == 'doc':
            create_doctor(user_profile)
        elif usertype == 'user':
            create_skaa(user_profile)
        else:
            raise ValueError('Bad usertype: %s' % usertype)

        return ( user, { } )
        
@render_to('signin.html')
def signin(request, usertype='user'):
    """
    Shared view for both user login and doctor login
    
    usertype should be 'user' or 'doc'
    """

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
                user, tmp = create_user( request.POST['email'],
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

    return ret

#Nothing special here, we don't need to check if they are logged in or not#I'm just lazy and want to sign out, logic of this needs to be looked at
def signout(request):
    logout(request)   
    return redirect('/')

def associate_album(request, album, user):
    if album is not None:
        album.userprofile = user.get_profile()
        album.save()

    # Once it has a user, clear the session back out
    Album.clear_session_album(request)

def skaa_signin(request):
    # Don't use the word 'skaa' here -- it'll be visible in the html : )
    return signin(request, usertype='user')

def doc_signin(request):
    return signin(request, usertype='doc')


