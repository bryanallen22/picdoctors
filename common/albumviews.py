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

class Combination():
    def __init__(self):
        self.user_pics = []
        self.doc_pic = None
        self.messages = []
        self.group_id = -1

@login_required
@render_to('album.html')
def album(request, album_id):
    #SECURITY (Move to Decorator)
    #############################
    profile = get_profile_or_None(request)

    album = get_object_or_None(Album, pk=album_id)
    
    job = album.get_job_or_None()

    if not job:
        return redirect('/')

    if job.skaa != profile and job.doctor != profile:
        return redirect('/')

    #############################
    #############################
    groups = Group.get_album_groups(job.album)
    groupings = []
    for group in groups:
        picco = Combination()
        picco.user_pics = Pic.get_group_pics(group)
        picco.group_id = group.id
        docPicGroup = group.get_latest_doctor_pic()
        if len(docPicGroup) > 0:
            docPicGroup = docPicGroup[0]
            picco.doc_pic = docPicGroup.get_pic()
        groupings.append(picco)


    return {'job_id': job.id, 'groupings' : groupings}

