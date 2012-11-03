from annoying.decorators import render_to
from annoying.functions import get_object_or_None
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.utils import simplejson
from common.models import Job
from common.models import Album
from common.models import Group
from common.models import UserProfile
from common.models import Pic
from common.models import Charge
from common.functions import get_profile_or_None
from common.calculations import calculate_job_payout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from decimal import *

from common.jobs import get_job_infos_json, get_pagination_info, JobInfo
from common.jobs import Actions, Action, RedirectData, DynamicAction
from common.jobs import send_job_status_change, fill_job_info

import math
import pdb


#TODO @permissions required to be here...
@render_to('jobs.html')
def job_page(request, page=1):
    if request.user.is_authenticated():
        jobs = Job.objects.filter(skaa=request.user.get_profile()).order_by('created').reverse()
    else:
        #TODO they shouldn't ever get here based on future permissions
        jobs = []

    pager, cur_page = get_pagination_info(jobs, page)    

    job_infos_json = get_job_infos_json(cur_page, generate_skaa_actions, request)

    return {'job_infos_json':job_infos_json,
            'num_pages': range(1,pager.num_pages+1), 'cur_page': int(page), 
            'doc_page':False}

#get and fill up possible actions based on the status of this job
def generate_skaa_actions(job):
    ret = []

    #boring always created actions for populating below
    contact = DynamicAction('Contact Doctor', reverse('contact', args=[job.id]), True)

    #TODO remove pie, this is for fun and testing
    #i_like_pie = DynamicAction('I like Pie', 'i_like_pie')
    #u_like_pie = DynamicAction('Do You like Pie', '/u_like_pie')
    #ret.append(i_like_pie)
    #ret.append(u_like_pie)
    view_job_url= reverse('markup_album', args=[job.album.id, 1])
    view_job = DynamicAction('View Job', view_job_url, True)
    
    if job.status == Job.USER_SUBMITTED:
        pass
    elif job.status == Job.TOO_LOW:
        #Do something
        pass
    elif job.status == Job.DOCTOR_ACCEPTED:
        ret.append(contact)
        ret.append(view_job)
        #do something
    elif job.status == Job.DOCTOR_REQUESTS_ADDITIONAL_INFORMATION:
        ret.append(contact)
        ret.append(view_job)
        #do something
    elif job.status == Job.DOCTOR_SUBMITTED:
        ret.append(DynamicAction('Accept', '/accept_doctors_work/'))
        ret.append(view_job)
        ret.append(contact)
        ret.append(DynamicAction('Request Modification', '/request_modification/'))
        ret.append(DynamicAction('Request New Doctor', '/request_new_doctor/'))
        ret.append(DynamicAction('Reject', '/reject_doctors_work/'))
    elif job.status == Job.USER_ACCEPTED:
        ret.append(view_job)
        pass
    elif job.status == Job.USER_REQUESTS_MODIFICATION:
        ret.append(DynamicAction('Accept', '/accept_doctors_work/'))
        ret.append(view_job)
        ret.append(contact)
        ret.append(DynamicAction('Request New Doctor', '/request_new_doctor/'))
        ret.append(DynamicAction('Reject', '/reject_doctors_work/'))
        pass
    elif job.status == Job.USER_REJECTED:
        pass
    else:
        #How did we get here???
        pass

    return ret

        
def create_job(request, album, charge):
    j = None
    if album is not None:
        charge = generate_db_charge(charge)
        j = Job(skaa=request.user.get_profile(),
                album=album, 
                price_cents=charge.amount_cents, 
                charge=charge,
                status=Job.USER_SUBMITTED)
        
        j.save()       
        set_groups_locks(album, True)
    return j

def generate_db_charge(stripe_charge):
    charge = Charge(stripe_id=stripe_charge.id, 
                amount_cents=stripe_charge.amount, 
                fee_cents=stripe_charge.fee)
    charge.save()
    return charge

def set_groups_locks(album_to_lock, state):
    groups = Group.objects.filter(album=album_to_lock)
    #Performance Opportunity, just update all at once
    for group in groups:
        group.is_locked = state
        group.save()

@login_required
def accept_doctors_work(request):
    profile = get_profile_or_None(request)
    data = simplejson.loads(request.body)
    job = get_object_or_None(Job, id=data['job_id'])

    actions = Actions()
    actions.add('alert', 'There was an error processing your request.')
    if job and profile and job.skaa == profile:
        #TODO Put money into Doctors account 
        actions.clear()
        actions.add('alert', 'The job was accepted, and yet I didn\'t pay the doctor')
        job.status = Job.USER_ACCEPTED
        job.save()

        job_info = fill_job_info(job, generate_skaa_actions, profile)
        actions.addJobInfo(job_info)

        send_job_status_change(job, profile)

    return HttpResponse(actions.to_json(), mimetype='application/json')


@login_required
def reject_doctors_work(request):
    profile = get_profile_or_None(request)
    data = simplejson.loads(request.body)
    job = get_object_or_None(Job, id=data['job_id'])

    actions = Actions()
    actions.add('alert', 'There was an error processing your request.')
    if job and profile and job.skaa == profile:
        #TODO Put money into Doctors account 
        actions.clear()
        actions.add('alert', 'The job was rejected')
        job.status = Job.USER_REJECTED
        job.save()

        job_info = fill_job_info(job, generate_skaa_actions, profile)
        actions.addJobInfo(job_info)
        
        send_job_status_change(job, profile)

    return HttpResponse(actions.to_json(), mimetype='application/json')


@login_required
def request_modification(request):
    profile = get_profile_or_None(request)
    data = simplejson.loads(request.body)
    job = get_object_or_None(Job, id=data['job_id'])

    actions = Actions()
    actions.add('alert', 'There was an error processing your request.')
    if job and profile and job.skaa == profile:
        actions.clear()
        actions.add('alert', 'The user has requested modification')
        redir_url = reverse('contact', args=[job.id])
        r =  RedirectData(redir_url,'the communication page')
        actions.add('delay_redirect', r)
        job.status = Job.USER_REQUESTS_MODIFICATION
        job.save()
        send_job_status_change(job, profile)
        job_info = fill_job_info(job, generate_skaa_actions, profile)
        actions.addJobInfo(job_info)

    return HttpResponse(actions.to_json(), mimetype='application/json')






