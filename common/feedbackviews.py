from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from django.http import HttpResponse
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

import ipdb
import logging
import datetime
import settings

def feedback(request):
    data = simplejson.loads(request.body)
    profile = get_profile_or_None(request)

    from_whom = 'Cowardly Lion'
    tmp_from = data['from_whom'].strip()

    if profile:
        from_whom = profile.email
    elif tmp_from != '':
        from_whom = tmp_from
        
    feedback = data['user_feedback'].strip()
    success = False

    if feedback != '':
        success = send_feedback(from_whom, feedback)
        
    result = { 'success': success}

    response_data = simplejson.dumps(result)
    return HttpResponse(response_data, mimetype='application/json')

def send_feedback(from_whom, feedback):
    try:
        to_email = ['feedback@picdoctors.com']

        subject = from_whom + ' has some feedback'

        args = {'from':from_whom, 'feedback':feedback} 
        html_content = render_to_string('feedback_email.html', args)
                                        
        
        # this strips the html, so people will have the text
        text_content = strip_tags(html_content) 
        # create the email, and attach the HTML version as well.
        msg = EmailMultiAlternatives(subject, text_content, 'donotreply@picdoctors.com', to_email)
        msg.attach_alternative(html_content, "text/html")
        if settings.IS_PRODUCTION:
            sendAsyncEmail.apply_async(args=[msg])
        else:
            sendAsyncEmail(msg)

        return True
    except Exception as ex:
        return False

