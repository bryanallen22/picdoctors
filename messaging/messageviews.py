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

class Message():
    def __init__(self):
        self.commentor = None
        self.message = ''
        self.created = ''
        self.is_owner = False


class PicComment():
    def __init__(self):
        self.user_pics = []
        self.doc_pic = None
        self.messages = []
        self.group_id = -1
        self.sequence = 0

def prep_messages(base_messages, profile, job):
    """ get the information from either the job or the group message  """
    messages = []
    for msg in base_messages:
        message = Message()
        message.commentor = msg.commentor.user.username
        message.message = msg.message
        message.created = get_time_string(msg.created)
        message.is_owner = msg.commentor == job.skaa
        messages.append(message.__dict__)

    return simplejson.dumps(messages)

@login_required
@render_to('contact.html')
def contact(request, job_id):
    #SECURITY (Move to Decorator)
    #############################
    profile = get_profile_or_None(request)

    job = get_object_or_None(Job, pk=job_id)

    if not job:
        return redirect('/')

    if not (job.skaa == profile or job.doctor == profile or
        ( profile.is_doctor and job.status == Job.IN_MARKET)):
        return redirect('/')

    #############################
    #############################

    job_messages = prep_messages(JobMessage.get_messages(job), profile, job)

    return {'job_id': job.id, 'is_owner': (profile == job.skaa), 'job_messages' : job_messages}

#TODO  fix this so that it actually checks
def can_add_message(request):
    return True

def message_handler(request):
    result = {}
    if request.method == 'POST':
        data = simplejson.loads(request.body)
        message = data['message'].strip()
        if can_add_message(request) and message != '':
            profile = get_profile_or_None(request)
            msg = None
            group_val = data['group_id'].strip()
            job_val = data['job_id'].strip()

            job = get_object_or_None(Job, id=int(job_val))

            if group_val != '':
                group = get_object_or_None(Group, id=int(group_val))
                msg = GroupMessage()
                msg.group = group
            else:
                msg = JobMessage()
            
            msg.job = job
            msg.message = message
            msg.commentor = profile
            msg.save()

            job.last_communicator = profile
            job.save()


            generate_message_email(job, profile, msg)


    response_data = simplejson.dumps(result)
    return HttpResponse(response_data, mimetype='application/json')


def generate_message_email(job, profile, message):
    try:
        if message.commentor == job.skaa:
            from_whom = 'User'
            to_email = get_doctor_emails(job, message)
        else:
            from_whom = 'Doctor'
            to_email = [job.skaa.user.email]

        if len(to_email) == 0:
            return

        subject = 'The ' + from_whom + ' commented on your job'
        #Do I want to send the message to them, or make them go to the page?a
        args = {'from_whom':from_whom, 'job_id':job.id} 
        html_content = render_to_string('contact_email.html', args)
                                        
        
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
        #raise ex
        pass

def get_doctor_emails(job, message):
    ret = []
    # if there is a job doctor, only reply to him
    if job.doctor:
        ret.append(job.doctor.user.email)
    # no job doctor yet, reply to all doctors who have commented
    else:
        jms = JobMessage.objects.filter(job=job)
        for jm in jms:
            # skip users, and only add unique doctors
            if jm.commentor != job.skaa and jm.commentor.user.email not in ret:
                ret.append(jm.commentor.user.email)

    return ret

