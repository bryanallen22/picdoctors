from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.utils import simplejson

from annoying.decorators import render_to
from annoying.functions import get_object_or_None

from common.models import Job, Album, Group, Pic
from messaging.messageviews import prep_messages
from messaging.models import JobMessage, GroupMessage
from common.functions import get_profile_or_None, get_time_string
from django.utils.html import strip_tags
from common.decorators import require_login_as
from common.jobs import send_job_status_change

import ipdb
import logging
import datetime

class Combination():
    def __init__(self):
        self.user_pics = []
        self.max_height = -1
        self.max_width = -1
        self.doc_pic = None
        self.messages = []
        self.group_id = -1

@render_to('album.html')
def album(request, album_id):
    #SECURITY (Move to Decorator)
    #############################
    profile = get_profile_or_None(request)

    album = get_object_or_None(Album, pk=album_id)
    
    job = album.get_job_or_None()

    if not job:
        return redirect( reverse('permission_denied') )

    if not profile and not album.allow_publicly:
        return redirect( reverse('permission_denied') )

    moderator = False if not profile else profile.has_common_perm('album_approver')

    # if you are not the owner and not the doctor and not the moderator why are you here? (And it's not public, of course)
    if job.skaa != profile and job.doctor != profile and not moderator and not album.allow_publicly:
        return redirect('/')

    #############################
    #############################

    user_acceptable = job.status == Job.DOCTOR_SUBMITTED and job.skaa == profile and job.is_approved()

    groups = Group.get_album_groups(job.album)
    groupings = []
    for group in groups:
        picco = Combination()
        picco.user_pics = Pic.get_group_pics(group)
        picco.messages = prep_messages(GroupMessage.get_messages(group), job)
        for x in picco.user_pics:
            picco.max_height = max(picco.max_height, x.preview_height)
            picco.max_width = max(picco.max_width, x.preview_width)
        picco.group_id = group.id
        docPicGroup = group.get_latest_doctor_pic(job, profile)
        if len(docPicGroup) > 0:
            docPicGroup = docPicGroup[0]
            picco.doc_pic = docPicGroup.get_pic(profile, job)
            picco.max_height = max(picco.max_height, picco.doc_pic.preview_height)
            picco.max_width = max(picco.max_width, picco.doc_pic.preview_width)
        picco.group_id = group.id
            
        groupings.append(picco)

    can_view_comments = profile == job.skaa or \
                        profile == job.doctor or \
                        (profile and profile.isa('moderator'))

    return  {
            'job_id'            : job.id, 
            'user_acceptable'   : user_acceptable, 
            'is_owner'          : (profile == job.skaa), 
            'can_view_comments' : can_view_comments,
            'groupings'         : groupings,
            'is_public'         : album.allow_publicly,
            'shareable'         : job.status == Job.USER_ACCEPTED and job.skaa == profile,
    }

#This is for a moderator to approve an album
@require_login_as(['admin'])
def approve_album(request):
    profile = get_profile_or_None(request)
    data = simplejson.loads(request.body)
    job_id = data['job_id']
    job = get_object_or_None(Job, id=data['job_id'])

    # you also could say profile.isa('album_approver') but that doesn't make sense to me when I read it
    moderator =  profile.has_perm('common.album_approver')

    if job and job.album and moderator: # and moderator
        # only necessary for doctors that aren't auto_approve
        job.approved = True
        job.status = Job.DOCTOR_SUBMITTED
        job.save()

        send_job_status_change(request, job, None)

        update_doc_auto_approve(job)
    
    resp = simplejson.dumps({'redirect':reverse('album_approval_page')})
    return HttpResponse(resp, mimetype='application/json')

def update_doc_auto_approve(job):
    accepted_count = Job.objects.filter(doctor=job.doctor).filter(status=Job.USER_ACCEPTED).count()
    if accepted_count > 5:
        doc = job.doctor
        doc.auto_approve = True
        doc.save()

