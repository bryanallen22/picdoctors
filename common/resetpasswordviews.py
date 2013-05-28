from common.models import Profile

from annoying.decorators import render_to
from annoying.functions import get_object_or_None

from emailer.emailfunctions import send_email

import ipdb
import logging
import random
import string
import settings

def gen_password(length=12):
    """
    Generate a password
    """
    chars = string.ascii_letters + string.digits
    rand = random.SystemRandom()
    return ''.join([ rand.choice(chars) for x in range(length) ])

@render_to('reset_password.html')
def reset_password(request, email=None):
    """
    Only provide the 'email' parameter when faking emails
    """
    if request.method == 'GET':
        return { }
    elif request.method == 'POST':

        if not email and 'email' in request.POST:
            email = request.POST['email']

        if email:
            new_password = gen_password()

            user = get_object_or_None(Profile, email=email)
            if user:
                user.set_password(new_password)
                user.save()

                send_email(request,
                           email_address=email,
                           subject='Picdoctors password reset',
                           template_name='reset_password_email.html',
                           template_args={ 'new_password' : new_password }
                          )
        else:
            logging.debug('reset_password has no email in POST...')
            return { 'success' : False }

        return { 'success' : True }

        return { 'success' : True }

