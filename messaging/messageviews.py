from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.utils import simplejson

from annoying.decorators import render_to
from annoying.functions import get_object_or_None

from common.decorators import require_login_as
from common.functions import get_profile_or_None, get_time_string
from common.models import Job, Album, Group
from messaging.models import JobMessage, GroupMessage
from notifications.functions import notify
from notifications.models import Notification

import ipdb
import logging; log = logging.getLogger('pd')
import datetime
import settings

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

def build_messages(base_messages, user):

    messages = []
    for msg in base_messages:
        message = Message()
        message.commentor = msg.commentor.nickname
        message.message = msg.message
        message.created = get_time_string(msg.created)
        message.is_owner = msg.commentor == user
        message.id = msg.id
        messages.append(message.__dict__)

    return messages

def prep_messages(base_messages, user):
    """ get the information from either the job or the group message  """
    messages = build_messages(base_messages, user)

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

    job_messages = prep_messages(JobMessage.get_messages(job), profile)

    return {'job_id': job.id, 'is_owner': (profile == job.skaa), 'job_messages' : job_messages}

def can_add_message(profile, job):
    if not job:
        return False

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
        group_val = data['group_id'].strip()
        profile = get_profile_or_None(request)
        msg = generate_message(profile, message, job_val, group_val)

    response_data = simplejson.dumps(result)
    return HttpResponse(response_data, mimetype='application/json')

def generate_message(profile, message, job_id, group_id):
    job = get_object_or_None(Job, id=int(job_id))

    if can_add_message(profile, job) and message != '':
        msg = None

        if group_id != '':
            group_id = int(group_id)
            group = get_object_or_None(Group, id=group_id)
            msg = GroupMessage()
            msg.group = group
        else:
            log.error("JobMessage() is not ready for prime time any more...")
            #msg = JobMessage()

        msg.job = job
        msg.message = message
        msg.commentor = profile
        msg.save()

        job.last_communicator = profile
        job.save()

        return msg
    return None




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

