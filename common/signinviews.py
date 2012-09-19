from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.db import IntegrityError

from annoying.decorators import render_to

from skaa.uploadviews import get_batch_id
from common.models import Batch

import pdb
import logging
import datetime

def auth(email, password):
    """
    Authenticate the user.

    Possible return values:
        { } -- Everything good
        { 'bad_email_or_password' : True } -- Self explanatory
    """
    user = authenticate(username=email, password=password)
    if user is not None and user.is_active:
        return { }
    return { 'bad_email_or_password' : True }

def create_user(email, password, confirm_password):
    """
    Create the user.
    
    If the email is taken and the password matches that 
    email, just be nice and log them in.

    Possible return values:
        { } -- Everything good
        { 'email_already_exists'  : True } -- Email address taken, and the password didn't match
        { 'passwords_didnt_match' : True } -- Self explanatory
    """

    if password != confirm_password:
        return { 'passwords_didnt_match' : True }

    if User.objects.filter(email=email).count() > 0:
        # Username exists... Can we log in?
        if auth(email, password):
            # Error with those credentials
            return { 'email_already_exists' : True }
    else:
        user = User.objects.create_user(username=email, email=email, password=password)
        # TODO - create profile
        return { }
        
@render_to('signin.html')
def signin(request):
    # Set defaults here. Overridden below if necessary
    ret = { }

    if request.method == 'GET':
        # Nothing to do here now...
        ret = { }

    elif request.method == 'POST':

        # Sign into existing account
        if request.POST['create_acct_radio'] == 'have':
            ret = auth( request.POST['email'], request.POST['password'] )

        # Create a new account
        else:
            ret = create_user( request.POST['email'], request.POST['password'],
                               request.POST['confirm_password'] )

        if not ret:
            if 'remember' in request.POST.keys():
                # "Remember Me" is good for 30 days
                one_month = datetime.timedelta(days=30)
                request.session.set_expiry( one_month )
            else:
                # Session only good until browser closes
                request.session.set_expiry(0)

            return redirect('http://zombo.com')
        else:
            # Prepopulate the email address for them
            ret['email'] = request.POST['email']

    return ret

