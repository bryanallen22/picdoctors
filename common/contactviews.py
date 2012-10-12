from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.utils import simplejson

from annoying.decorators import render_to
from annoying.functions import get_object_or_None

from common.models import Job, Batch, Group, Pic
from common.models import JobMessage, GroupMessage
from common.functions import get_profile_or_None, get_time_string

import pdb
import logging
import datetime

class Message():
    def __init__(self):
        self.id = -1
        self.commentor = None
        self.message = ''
        self.date = ''

class PicComment():
    def __init__(self):
        self.user_pics = []
        self.doc_pic = None
        self.messages = []
        self.group_id = -1

# still haven't tested it, the essential hope is the shared model
# will allow me to just send it in here and I can suck info out
def prep_messages(base_messages):
    messages = []
    for msg in base_messages:
        message = Message()
        message.id = msg.id
        message.commentor = msg.commentor
        message.message = msg.message
        message.date = get_time_string(msg.created)
        messages.append(message)

    return messages

@login_required
@render_to('contact.html')
def contact(request, job_id):
    #SECURITY (Move to Decorator)
    #############################
    profile = get_profile_or_None(request)

    job = get_object_or_None(Job, pk=job_id)

    if not job:
        return redirect('/')

    if job.skaa != profile and job.doctor != profile:
        return redirect('/')

    #############################
    #############################

    job_messages = prep_messages(JobMessage.get_messages(job))

    groups = Group.get_batch_groups(job.batch)
    group_messages = []
    for group in groups:
        picco = PicComment()
        picco.user_pics = Pic.get_group_pics(group)
        picco.group_id = group.id
        docPicGroup = group.get_latest_doctor_pic()
        if len(docPicGroup) > 0:
            docPicGroup = docPicGroup[0]
            picco.doc_pic = docPicGroup.get_pic()
        picco.messages = prep_messages(GroupMessage.get_messages(group))
        group_messages.append(picco)


    return {'job_id': job.id, 'job_messages' : job_messages, 'group_messages' : group_messages}

@login_required
def post_message(request):
    data = simplejson.loads(request.body)
    job_id = int(data['job_id'])
    group_id = int(data['group_id'])
    message = data['message']

    message = message.strip()
    if message == '':
        return {}
    if not job_id:
        return {}

    job = get_object_or_None(Job, id=job_id)
    profile = get_profile_or_None(request)

    if job and profile and job.is_part_of(profile):
        group = get_object_or_None(Group, id=group_id)
        g = GroupMessage()
        g.commentor = profile
        g.message = message
        g.group = group
        g.save()

    result = {}
    response_data = simplejson.dumps(result)
    return HttpResponse(response_data, mimetype='application/json')

