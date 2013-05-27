from common.models import Profile
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.template import RequestContext

from annoying.decorators import render_to
from annoying.functions import get_object_or_None

from tasks.tasks import sendAsyncEmail

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

                subject = 'Picdoctors password reset'

                args = { 'new_password' : new_password }
                html_content  = render_to_string('reset_password_email.html', args, RequestContext(request))
                text_content  = "Your password has been changed to %s.\n\n" % new_password
                text_content += "You can log in here: http://picdoctors.com/signin/"
                msg = EmailMultiAlternatives( subject, text_content, 'contact@picdoctors.com',
                                              [email] )
                msg.attach_alternative(html_content, "text/html")

                if settings.IS_PRODUCTION:
                    sendAsyncEmail.apply_async(args=[msg])
                else:
                    sendAsyncEmail(msg)

        else:
            logging.debug('reset_password has no email in POST...')
            return { 'success' : False }

        return { 'success' : True }

        return { 'success' : True }

