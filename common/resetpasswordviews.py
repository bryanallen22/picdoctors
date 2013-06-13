from annoying.decorators import render_to
from annoying.functions import get_object_or_None
from common.models import Profile
from emailer.emailfunctions import send_email

import ipdb
import logging; log = logging.getLogger('pd')
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
def reset_password(request):
    """
    Only provide the 'email' parameter when faking emails
    """
    if request.method == 'GET':
        return { }
    elif request.method == 'POST':

        success = False
        if 'email' in request.POST:
            email = request.POST['email']
            new_password = gen_password()

            user = get_object_or_None(Profile, email=email)
            if user:
                user.set_password(new_password)
                user.save()

                success = send_email(request,
                                     email_address=email,
                                     template_name='reset_password_email.html',
                                     template_args={ 'new_password' : new_password }
                                    )
        return {
                'success'     : success,
                'email_error' : not success,
               }
