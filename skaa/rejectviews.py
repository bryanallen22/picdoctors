from django.contrib.auth.decorators import login_required
from annoying.decorators import render_to
from common.models import Group
from django.utils import simplejson
from annoying.functions import get_object_or_None
from common.functions import get_profile_or_None
from common.models import Job
from common.jobs import send_job_status_change
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import redirect

import pdb

@login_required
@render_to("reject.html")
def refund(request, job_id):

    if not reject_belongs(request, job_id):
        return redirect('/')

    return  {
            'job_id'        : job_id, 
            'is_refund'     : True,
            }


@login_required
@render_to("reject.html")
def switch_doctor(request, job_id):

    if not reject_belongs(request, job_id):
        return redirect('/')

    return  {
            'job_id'        : job_id, 
            'is_refund'     : False,
            }

def reject_belongs(request, job_id):
    profile = get_profile_or_None(request)
    job = get_object_or_None(Job, id=job_id)

    if not job or not profile:
        return False

    if job.skaa != profile:
        return False

    return True

@login_required
def refund_user_endpoint(request):
    profile = get_profile_or_None(request)
    data = simplejson.loads(request.body)
    job = get_object_or_None(Job, id=data['job_id'])

    if job and profile and job.skaa == profile:
        #TODO Refund User
        job.status = Job.REFUND
        job.save()

        send_job_status_change(job, profile)

    result = { 'relocate' : reverse('job_page') }
    response_data = simplejson.dumps(result)
    return HttpResponse(response_data, mimetype='application/json')

@login_required
def switch_doctor_endpoint(request):
    profile = get_profile_or_None(request)
    data = simplejson.loads(request.body)
    job = get_object_or_None(Job, id=data['job_id'])


    if job and profile and job.skaa == profile:
        job.status = Job.IN_MARKET
        job.ignore_last_doctor = job.doctor     
        job.doctor = None
        job.approved = False
        job.payout_price_cents = 0
        job.save()
        
        groups = Group.get_job_groups(job)

        for group in groups:
            group.delete_doctor_pics()

        send_job_status_change(job, profile)

    result = { 'relocate' : reverse('job_page') }
    response_data = simplejson.dumps(result)
    return HttpResponse(response_data, mimetype='application/json')

