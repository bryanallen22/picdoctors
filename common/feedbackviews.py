from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.utils import simplejson

from annoying.decorators import render_to
from annoying.functions import get_object_or_None

from common.models import Job, Album, Group, Pic
from messaging.models import JobMessage, GroupMessage
from common.functions import get_profile_or_None, get_time_string
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from tasks.tasks import sendAsyncEmail

import pdb
import logging
import datetime

@login_required
def feedback(request):
    data = simplejson.loads(request.body)
    profile = get_profile_or_None(request)
    feedback = data['user_feedback'].strip()

    if feedback != '':
        send_feedback(profile, feedback)
        
    result = {}

    response_data = simplejson.dumps(result)
    return HttpResponse(response_data, mimetype='application/json')

def send_feedback(profile, feedback):
    try:
        from_whom = profile.user.username
        to_email = ['feedback@picdoctors.com']

        subject = 'A user has some feedback'

        args = {'from':from_whom, 'feedback':feedback} 
        html_content = render_to_string('feedback_email.html', args)
                                        
        
        # this strips the html, so people will have the text
        text_content = strip_tags(html_content) 
        # create the email, and attach the HTML version as well.
        msg = EmailMultiAlternatives(subject, text_content, 'donotreply@picdoctors.com', to_email)
        msg.attach_alternative(html_content, "text/html")
        #TODO if you want to switch to using the workers
        # sendAsyncEmail.apply_async(args=[msg])
        sendAsyncEmail(msg)

#        send_mail(subject, message , 'donotreply@picdoctors.com', [other_user_email], fail_silently=False)
    except Exception as ex:
        raise ex

