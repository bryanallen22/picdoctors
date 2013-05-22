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
from django.template import RequestContext
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
        logged_in = True
    elif tmp_from != '':
        from_whom = tmp_from
        logged_in = False
        
    feedback = data['user_feedback'].strip()
    success = False

    if feedback != '':
        success = send_feedback(request, from_whom, feedback, logged_in)
        
    result = { 'success': success}

    response_data = simplejson.dumps(result)
    return HttpResponse(response_data, mimetype='application/json')

def send_feedback(request, from_whom, feedback, logged_in, to_email=None):
    """
    Only provide to_email when faking emails
    """
    try:
        to_email = [to_email] or ['feedback@picdoctors.com']

        subject = from_whom + ' has some feedback'

        args = {'from':from_whom, 'feedback':feedback, 'logged_in':logged_in} 
        html_content = render_to_string('feedback_email.html', args, RequestContext(request))
                                        
        
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

