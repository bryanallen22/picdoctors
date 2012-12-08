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
from common.models import BPHoldWrapper
from common.functions import get_profile_or_None
from common.calculations import calculate_job_payout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from decimal import *

from common.jobs import get_job_infos_json, get_pagination_info, JobInfo
from common.jobs import Actions, Action, RedirectData, DynamicAction
from common.jobs import send_job_status_change, fill_job_info

import math
import ipdb


@login_required
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
            'reverser': 'job_page_with_page', 'doc_page':False, 'title': 'My Jobs'}

#get and fill up possible actions based on the status of this job
def generate_skaa_actions(job):
    ret = []

    #boring always created actions for populating below
    contact = DynamicAction('Job Questions', reverse('contact', args=[job.id]), True)
    view_markup_url= reverse('markup_album', args=[job.album.id, 1])
    view_markup = DynamicAction('View Markups', view_markup_url, True)
    view_album = DynamicAction('View Album', reverse('album', args=[job.album.id]), True)
    accept_album = DynamicAction('Accept Work', reverse('accept_work', args=[job.id]), True)
    refund = DynamicAction('Request Refund', reverse('refund', args=[job.id]), True)
    switch_doc = DynamicAction('Switch Doctor', reverse('switch_doctor', args=[job.id]), True)
    
    if job.status == Job.IN_MARKET:
        ret.append(contact)
        ret.append(view_album)
        ret.append(refund)

    elif job.status == Job.TOO_LOW:
        pass

    elif job.status == Job.DOCTOR_ACCEPTED:
        ret.append(contact)
        ret.append(view_album)
        ret.append(switch_doc)
        ret.append(refund)

    elif job.status == Job.MODERATOR_APPROVAL_NEEDED:
        ret.append(contact)
        ret.append(view_album)
        ret.append(switch_doc)
        ret.append(refund)

    elif job.status == Job.DOCTOR_SUBMITTED:
        ret.append(accept_album)
        ret.append(contact)
        ret.append(view_album)
        ret.append(switch_doc)
        ret.append(refund)

    elif job.status == Job.USER_ACCEPTED:
        ret.append(view_album)

   # elif job.status == Job.USER_REQUESTS_MODIFICATION:
   #     ret.append(accept_album)
   #     ret.append(contact)
   #     ret.append(view_album)
   #     ret.append(switch_doc)
   #     ret.append(refund)

    elif job.status == Job.USER_REJECTED:
        pass

    else:
        #How did we get here???
        pass

    return ret

def create_job(profile, album, hold):
    j = None
    bp_hold_wrapper = BPHoldWrapper(uri=hold.uri, cents=hold.amount)
    bp_hold_wrapper.save()
    if album is not None:
        j = Job(skaa=profile,
                album=album, 
                price_cents=hold.amount,
                bp_hold_wrapper=bp_hold_wrapper,
                status=Job.IN_MARKET)
        
        j.save()

        set_groups_locks(album, True)
    return j

#TODO this is pointless, you could delete this stuff... you never use it...
def set_groups_locks(album_to_lock, state):
    groups = Group.objects.filter(album=album_to_lock)
    #Performance Opportunity, just update all at once
    for group in groups:
        group.is_locked = state
        group.save()


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






