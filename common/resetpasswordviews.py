from common.models import Profile
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from annoying.decorators import render_to
from annoying.functions import get_object_or_None

from tasks.tasks import sendAsyncEmail

import ipdb
import logging
import random
import string

def gen_password(length=12):
    """
    Generate a password
    """
    chars = string.ascii_letters + string.digits
    rand = random.SystemRandom()
    return ''.join([ rand.choice(chars) for x in range(length) ])

@render_to('reset_password.html')
def reset_password(request):
    if request.method == 'GET':
        return { }
    elif request.method == 'POST':
        if 'email' in request.POST:
            new_password = gen_password()

            user = get_object_or_None(Profile, email=request.POST['email'])
            if user:
                user.set_password(new_password)
                user.save()

                subject = 'Picdoctors password reset'

                args = { 'new_password' : new_password }
                html_content  = render_to_string('reset_password_email.html', args)
                text_content  = "Your password has been changed to %s.\n\n" % new_password
                text_content += "You can log in here: http://picdoctors.com/signin/"
                msg = EmailMultiAlternatives( subject, text_content, 'donotreply@picdoctors.com',
                                              [request.POST['email']] )
                msg.attach_alternative(html_content, "text/html")

                sendAsyncEmail(msg)
        else:
            pass

        return { 'success' : True }

