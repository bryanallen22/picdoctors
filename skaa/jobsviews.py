from annoying.decorators import render_to
from annoying.functions import get_object_or_None
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.utils import simplejson
from common.models import Job
from common.models import Album
from common.models import Group
from common.models import Pic
from common.balancedmodels import BPHold
from common.functions import get_profile_or_None, get_datetime
from common.calculations import calculate_job_payout
from decimal import *

from common.jobs import get_job_infos_json, get_pagination_info, JobInfo
from common.jobs import Actions, Action, RedirectData, AlertData, DynamicAction
from common.jobs import send_job_status_change, fill_job_info
from common.decorators import require_login_as
from datetime import timedelta
import datetime
from django.utils.timezone import utc

import math
import ipdb



@require_login_as(['skaa', 'doctor'])
@render_to('jobs.html')
def job_page(request, page=1, job_id=None):
    ### get a list of the jobs by this user ###
    if request.user.is_authenticated():
        if job_id:
            jobs = Job.objects.filter(skaa=request.user).filter(id=job_id).order_by('created').reverse()
        else:
            jobs = Job.objects.filter(skaa=request.user).order_by('created').reverse()
    else:
        jobs = []

    update_old_jobs(jobs)

    pager, cur_page = get_pagination_info(jobs, page)    

    job_infos_json = get_job_infos_json(cur_page, generate_skaa_actions, request)

    return {
            'job_infos_json'   : job_infos_json,
            'num_pages'        : range(1,pager.num_pages+1), 
            'cur_page'         : int(page), 
            'reverser'         : 'job_page_with_page', 
            'doc_page'         : False, 
            'title'            : 'My Jobs',
    }

# if a job ends up being older 7 days, we change the state to
# you suck, and need to up the price or something
# What a bummer for them, but not my problem
def update_old_jobs(list_of_jobs):

    if not list_of_jobs or len(list_of_jobs)==0:
        return

    now = get_datetime()
    # just to let future you know, there is an hour period where the job
    # has been removed, but won't get updated to out of market if
    # they hit this page, but I don't feel bad about that
    seven_days_ago = now - timedelta(days=7)

    for job in list_of_jobs:
        if job.bp_hold.created < seven_days_ago and job.status == Job.IN_MARKET:
            job.status=Job.OUT_OF_MARKET
            job.save()
            # TODO we may need to do other things in the future
            

# get and fill up possible actions based on the status of this job
def generate_skaa_actions(job):
    ret = []

    url_redirect=True

    #boring always created actions for populating below
    contact = DynamicAction('Job Questions', reverse('contact', args=[job.id]), url_redirect)
    view_markup_url= reverse('markup_album', args=[job.album.id, 1])
    view_markup = DynamicAction('View Markups', view_markup_url, url_redirect)
    view_album = DynamicAction('View Album', reverse('album', args=[job.album.id]), url_redirect)
    accept_album = DynamicAction('Accept Work', reverse('accept_work', args=[job.id]), url_redirect)
    refund = DynamicAction('Request Refund', reverse('refund', args=[job.id]), url_redirect)
    switch_doc = DynamicAction('Switch Doctor', reverse('switch_doctor', args=[job.id]), url_redirect)
    increase_price = DynamicAction('Increase Price', reverse('increase_price', args=[job.id]), url_redirect)
    place_back_in_market = DynamicAction('Return to Market', reverse('increase_price', args=[job.id]), url_redirect)
    share_album = DynamicAction('Share Album', reverse('make_album_shareable', args=[job.id]))
    unshare_album = DynamicAction('Unshare Album', reverse('make_album_unshareable', args=[job.id]))
    
    if job.status == Job.IN_MARKET:
        ret.append(contact)
        ret.append(view_album)
        ret.append(increase_price)
        ret.append(refund)

    elif job.status == Job.DOCTOR_ACCEPTED:
        ret.append(contact)
        ret.append(view_album)
        ret.append(switch_doc) # in case the doc takes too long
        ret.append(refund)

    elif job.status == Job.MODERATOR_APPROVAL_NEEDED:
        ret.append(contact)
        ret.append(view_album)
        #ret.append(switch_doc) -- bryan removed: they haven't seen his work yet, let's not let them reject this guy yet
        ret.append(refund)

    elif job.status == Job.DOCTOR_SUBMITTED:
        ret.append(accept_album)
        ret.append(contact)
        ret.append(view_album)
        ret.append(switch_doc)
        ret.append(refund)

    elif job.status == Job.USER_ACCEPTED:
        ret.append(view_album)
        if job.album.allow_publicly:
            ret.append(unshare_album)
        else:
            ret.append(share_album)

    elif job.status == Job.OUT_OF_MARKET:
        ret.append(increase_price)

    elif job.status == Job.REFUND:
        ret.append(place_back_in_market)
        pass

    else:
        #How did we get here???
        pass

    return ret
    

# when the user sets a price, we create a job
def create_job(profile, album, hold):
    job = None
    bp_hold= BPHold(uri=hold.uri, cents=hold.amount)
    bp_hold.save()
    if album is not None:
        job = Job(skaa=profile,
                album=album, 
                bp_hold=bp_hold,
                status=Job.IN_MARKET)
        
        job.save()

        set_groups_locks(album, True)

    return job


# When a user increases the price of a job
# we call this method to update the hold
def update_job_hold(job, hold):
    bp_hold = BPHold(uri=hold.uri, cents=hold.amount)
    bp_hold.save()

    if job.bp_hold:
        job.bp_hold.delete()

    job.bp_hold = bp_hold
    job.save()

    return job

# We mostly use this for finding out when things are read_only etc
def set_groups_locks(album_to_lock, state):
    groups = Group.objects.filter(album=album_to_lock)
    # Performance Opportunity, just update all at once, in fact
    # the line below would do it, but then I think that skips 
    # the modified date time update
    # Group.objects.filter(album=album_to_lock).update(is_locked=state)
    for group in groups:
        group.is_locked = state
        group.save()

@require_login_as(['skaa'])
def request_modification(request):
    profile = get_profile_or_None(request)
    data = simplejson.loads(request.body)
    job = get_object_or_None(Job, id=data['job_id'])

    actions = Actions()
    actions.add('alert', AlertData('There was an error processing your request.', 'error'))
    if job and profile and job.skaa == profile:
        actions.clear()
        actions.add('alert', AlertData('The user has requested modification', 'success'))
        redir_url = reverse('contact', args=[job.id])
        r =  RedirectData(redir_url,'The Communication Page')
        actions.add('action_button', r)
        job.status = Job.USER_REQUESTS_MODIFICATION
        job.save()
        send_job_status_change(request, job, profile)
        job_info = fill_job_info(job, generate_skaa_actions, profile)
        actions.addJobInfo(job_info)

    return HttpResponse(actions.to_json(), mimetype='application/json')


@require_login_as(['skaa'])
def make_album_shareable(request, job_id):
    profile = get_profile_or_None(request)
    job = get_object_or_None(Job, id=job_id)

    return make_album_public(True, 'The album is now public and can be shared!', job, profile)

@require_login_as(['skaa'])
def make_album_unshareable(request, job_id):
    profile = get_profile_or_None(request)
    job = get_object_or_None(Job, id=job_id)

    return make_album_public(False, 'The album is now private and cannot be shared', job, profile)


def make_album_public(to_public, success_message, job, profile):

    actions = Actions()

    try:
        if job and job.album and profile and job.skaa == profile: 
            alb = job.album
            alb.allow_publicly = to_public
            alb.save()
            status = success_message
            actions.clear()
            actions.add('alert', AlertData(success_message, 'success'))
    
            job_info = fill_job_info(job, generate_skaa_actions, profile)
            actions.addJobInfo(job_info)
    except:
        actions.clear()
        actions.add('alert', AlertData('There was an error processing your request.', 'error'))
        
    return HttpResponse(actions.to_json(), mimetype='application/json')
