from django.shortcuts import render_to_response, redirect
from django.core.urlresolvers import reverse
from django.utils import simplejson
from django.http import HttpResponse
from django.contrib.auth.models import User

from annoying.decorators import render_to
from annoying.functions import get_object_or_None
from common.functions import get_profile_or_None
from django.contrib.auth.decorators import login_required

from common.models import Album, Group, Job, UserProfile
from common.jobs import send_job_status_change

import pdb
import logging
import datetime

@login_required
@render_to('accept_work.html')
def accept_work(request, job_id):
    profile = get_profile_or_None(request)
    job = get_object_or_None(Job, id=job_id)
    if job.skaa != profile:
        redirect('/')

    return {'job_id':job_id}


@login_required
def accept_doctors_work(request):
    profile = get_profile_or_None(request)
    data = simplejson.loads(request.body)
    job = get_object_or_None(Job, id=data['job_id'])

    if job and profile and job.skaa == profile:
        #TODO Put money into Doctors account 
        job.status = Job.USER_ACCEPTED
        job.save()
        groups = Group.get_album_groups(job.album)

        for group in groups:
            group.accept_doctor_pics()

        send_job_status_change(job, profile)

    result = { 'relocate' : reverse('album', args=[job.album.id]) }
    response_data = simplejson.dumps(result)
    return HttpResponse(response_data, mimetype='application/json')

