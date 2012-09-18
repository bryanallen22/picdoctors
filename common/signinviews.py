from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate

from annoying.decorators import render_to

from skaa.uploadviews import get_batch_id
from common.models import Batch

import pdb
import logging

def auth(email, passw):
    """ Authenticate the user. Return True if successful. """
    user = authenticate(username=email, password=passw)
    if user is not None and user.is_active:
        return True
    return False

def create_user(email, password):
    """ Create the user.
    
        If the email is taken and the password matches that 
        email, just be nice and log them in. If the email is
        taken and the password does not match, return False"""
    try:
        user = User.objects.create_user(email, email, password)
        user.save()
        return True
    except:
        return False

@render_to('signin.html')
def signin(request):
    # Set defaults here. Overridden below if necessary
    ret = {
        'bad_email_or_password' : False,
        'passwords_didnt_match' : False,
    }

    if request.method == 'GET':
        # Nothing to do here now...
        pass

    elif request.method == 'POST':

        # Sign into existing account
        if request.POST['create_acct_radio'] == 'have':
            if auth(request.POST['email'], request.POST['password']):
                return redirect('http://zombo.com')
            else:
                ret['bad_email_or_password'] = True

        # Create a new account
        else:
            if request.POST['password'] == request.POST['confirm_password']:
                # Actually create the user
                if create_user(request.POST['email'], request.POST['password']):
                    return redirect('http://zombo.com')
                else:
                    ret['bad_email_or_password'] = True
            else:
                ret['passwords_didnt_match'] = True

    return ret

