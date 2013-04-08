from django.shortcuts import render_to_response, redirect
from django.core.urlresolvers import reverse
from django.utils import simplejson
from django.http import HttpResponse
from django.contrib.auth.models import User

from annoying.decorators import render_to
from annoying.functions import get_object_or_None
from common.functions import get_profile_or_None, get_datetime
from common.balancedfunctions import get_merchant_account
from django.contrib.auth.decorators import login_required

from common.models import Album, Group, Job, DocRating
from common.jobs import send_job_status_change
from common.balancedfunctions import *

import ipdb
import logging
from datetime import datetime
import pytz

@login_required
@render_to('accept_work.html')
def accept_work(request, job_id):

    profile = get_profile_or_None(request)
    job = get_object_or_None(Job, id=job_id)

    if job.skaa != profile or job.status != Job.DOCTOR_SUBMITTED:
        return redirect('/')

    if request.method == 'POST':
        if job and profile and job.skaa == profile:
            if 'allow_publicly' in request.POST:
                if request.POST['allow_publicly'] == 'allow':
                    job.album.allow_publicly = True
                    job.album.save()
            else:
                # Return some kind of error
                return { 'job_id':job_id, 'allowpublic_error':True }

            do_debit(request, profile, job)

            job.status = Job.USER_ACCEPTED
            job.accepted_date = get_datetime()
            job.save()

            # Update Doctor Approval Count (for use in figuring out how much $$/job)
            job.doctor.get_approval_count(True)
            
            dr = DocRating()
            dr.doctor = job.doctor
            dr.job = job
            dr.overall_rating = get_rating(request)
            dr.comments = request.POST['comment']
            dr.save()

            send_job_status_change(job, profile)

            return redirect(reverse('album', args=[job.album.id]))

    return {'job_id':job_id}

def get_rating(request):
    rating = 1
    try:
        rating = int(request.POST['rating_val'])
    except ValueError:
        rating = 1 
    # Make sure between 1 and 5
    rating = min(5, rating)
    rating = max(1, rating)

    return rating
