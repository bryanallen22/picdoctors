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
import settings
from notifications.functions import notify
from notifications.models import Notification
from common.decorators import require_login_as

import ipdb
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

def prep_messages(base_messages, job):
    """ get the information from either the job or the group message  """
    messages = []
    for msg in base_messages:
        message = Message()
        message.commentor = msg.commentor.nickname
        message.message = msg.message
        message.created = get_time_string(msg.created)
        message.is_owner = msg.commentor == job.skaa
        messages.append(message.__dict__)

    return simplejson.dumps(messages)

@require_login_as(['skaa', 'doctor'])
@render_to('contact.html')
def contact(request, job_id):
    #SECURITY (Move to Decorator)
    #############################
    profile = get_profile_or_None(request)

    job = get_object_or_None(Job, pk=job_id)

    if not job:
        return redirect('/')

    if not (job.skaa == profile or job.doctor == profile or
        ( profile.isa('doctor') and job.status == Job.IN_MARKET)):
        return redirect('/')

    #############################
    #############################

    job_messages = prep_messages(JobMessage.get_messages(job), job)

    return {'job_id': job.id, 'is_owner': (profile == job.skaa), 'job_messages' : job_messages}

def can_add_message(request, job):
    if not job:
        return False

    profile = get_profile_or_None(request)
    
    if job.skaa == profile:
        return True

    if job.doctor == profile:
        return True

    if job.doctor == None and profile.isa('doctor'):
        return True

    return False

@require_login_as(['skaa', 'doctor'])
def message_handler(request):
    result = {}
    if request.method == 'POST':
        data = simplejson.loads(request.body)
        message = data['message'].strip()

        job_val = data['job_id'].strip()
        job = get_object_or_None(Job, id=int(job_val))

        if can_add_message(request, job) and message != '':
            profile = get_profile_or_None(request)
            msg = None
            group_val = data['group_id'].strip()

            job_msg = False

            if group_val != '':
                group_val = int(group_val)
                group = get_object_or_None(Group, id=group_val)
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
    job_message = isinstance(message, JobMessage)
    group_message = isinstance(message, GroupMessage)
    to_peeps = None

    if message.commentor == job.skaa:
        from_whom = job.skaa.nickname
        to_peeps = get_doctors(job, message)
    else:
        from_whom = job.doctor.nickname
        to_peeps = [job.skaa]

    if len(to_peeps) == 0:
        return

    job_no = str(job.id).rjust(8, '0') 

    if job_message:
        subject = 'Comment on job #' + job_no
        site_path = reverse('contact', args=[job.id])
    elif group_message:
        subject = 'Comment on a picture in job #' + job_no
        site_path = reverse('album', args=[job.album.id])

    the_message = from_whom + " said '" + message.message + "'"

    notify(Notification.JOB_MESSAGE, subject,  the_message, to_peeps, site_path) 

def get_doctors(job, message):
    ret = []
    # if there is a job doctor, only reply to him
    if job.doctor:
        ret.append(job.doctor)
    # no job doctor yet, reply to all doctors who have commented
    else:
        jms = JobMessage.objects.filter(job=job)
        for jm in jms:
            # skip users, and only add unique doctors
            if jm.commentor != job.skaa and jm.commentor not in ret:
                ret.append(jm.commentor)

    return ret

