from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

from annoying.decorators import render_to
from annoying.functions import get_object_or_None

from common.models import Job, Batch, Group, Pic
from common.models import JobMessage, GroupMessage
from common.functions import get_profile_or_None

import pdb
import logging
import datetime

# This class is 
class Comment():
    def __init__(self):
        self.id = -1
        self.message = ''
        self.date = ''

class PicComment():
    def __init__(self):
        self.user_pics = []
        self.doc_pic = None
        self.messages = []

# still haven't tested it, the essential hope is the shared model
# will allow me to just send it in here and I can suck info out
def prep_messages(base_messages):
    comments = []
    for msg in base_messages:
        com = Comment()
        com.id = msg.id
        com.message = msg.message
        com.date = msg.created
        comments.append(com)

    return comments

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
        picco.doc_pic = group.get_latest_doctor_pic()
        picco.messages = prep_messages(GroupMessage.get_messages(group))
        group_messages.append(picco)



    return {}
