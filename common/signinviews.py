from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.db import IntegrityError

from annoying.decorators import render_to

from skaa.uploadviews import get_batch_id
from common.models import Batch, UserProfile

import pdb
import logging
import datetime

def create_skaa(user):
    logging.info('Reached create_skaa')

def create_doctor(user):
    logging.info('Reached create_doctor')

def auth(email, password):
    """
    Authenticate the user.

    Possible return values:
        { } -- Everything good
        { 'bad_email_or_password' : True } -- Self explanatory
    """
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
        if usertype == 'doc':
            create_doctor(user)
        elif usertype == 'user':
            create_skaa(user)
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
    ret = { 'usertype' : usertype }

    if request.method == 'GET':
        # Nothing to do here now...
        pass

    elif request.method == 'POST':

        # Sign into existing account
        if request.POST['create_acct_radio'] == 'have':
            user, tmp = auth( request.POST['email'], request.POST['password'] )
            ret.update(tmp)

        # Create a new account
        else:
            user, tmp = create_user( request.POST['email'], request.POST['password'],
                                     request.POST['confirm_password'], usertype )
            ret.update(tmp)

        if user:
            # Successful login. Take care of "remember me" button
            login(request, user)
            if 'remember' in request.POST.keys():
                # "Remember Me" is good for 30 days
                one_month = datetime.timedelta(days=30)
                request.session.set_expiry( one_month )
            else:
                # Session only good until browser closes
                request.session.set_expiry(0)

            # Long term:
            #   -- People only get here because they tried to visit a page that required them to
            #      be logged in. Once they log in, they go to that page.
            # For now:
            #   -- Send skaa to set_price
            #   -- Send doctors to zombo.com
            if usertype == 'user':
                return redirect(reverse('set_price'))
            elif usertype == 'doc':
                return redirect('http://zombo.com')

        else:
            # Something went wrong. Let's at least prepopulate the email address for them
            ret['email'] = request.POST['email']

    return ret

def skaa_signin(request):
    # Don't use the word 'skaa' here -- it'll be visible in the html : )
    return signin(request, usertype='user')

def doc_signin(request):
    return signin(request, usertype='doc')


