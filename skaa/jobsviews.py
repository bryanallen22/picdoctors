from annoying.decorators import render_to
from annoying.functions import get_object_or_None
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.utils import simplejson
from common.models import Job
from common.models import Batch
from common.models import Group
from common.models import UserProfile
from common.models import Pic
from common.functions import get_profile_or_None
from common.calculations import calculate_job_payout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from decimal import *
import math
import pdb

class JobInfo:
    def __init__(self):
        self.job_id = '1'
        self.output_pic_count = ''
        self.status = 'Unknown'
        self.doctor_exists = False
        self.batch = -1
        self.batchurl = ''
        self.pic_thumbs = []
        self.dynamic_actions = []

        #doctor specific
        self.doctor_payout = ''

class DynamicAction:
    def __init__(self, text = '', url = '', redir=False):
        self.text = text
        self.url = url
        self.redir = redir


#TODO @permissions required to be here...
@render_to('jobs.html')
def job_page(request, page=1):
    #TODO implement paging
    if request.user.is_authenticated():
        jobs = Job.objects.filter(skaa=request.user.get_profile())
    else:
        #TODO they shouldn't ever get here based on future permissions
        jobs = []

    page_info = get_pagination_info(jobs, page)    
    pager = page_info['pager']
    cur_page = page_info['cur_page']


    job_infos = get_job_infos(cur_page, generate_skaa_actions, request)


    return { 'job_infos' :job_infos , 'num_pages': range(1,pager.num_pages+1), 'cur_page': int(page)}

#I should do error checking
def get_pagination_info(jobs, page):
    #this should be configurable! they maybe want to see 20 jobs...
    pager = Paginator(jobs, 5)
    
    cur_page = pager.page(page)

    return {'pager': pager, 'cur_page':cur_page }

#Populate job info based on job objects from database.
#job infos are a mixture of Pic, Job, & Batch
def get_job_infos(cur_page_jobs, action_generator, request):
    job_infos = []

    if cur_page_jobs is None:
        return job_infos

    for job in cur_page_jobs:
        job_inf = JobInfo()
        job_inf.job_id = job.id
        job_inf.status = job.get_status_display()
        job_inf.doctor_exists = job.doctor is not None
        batch = job.batch
        job_inf.dynamic_actions = action_generator(job, request)

        if job_inf.doctor_exists:
            #pull price from what we promised them
            job_inf.doctor_payout = job.payout_price
        else:
            job_inf.doctor_payout = calculate_job_payout(job, request.user.get_profile())

        #TODO I'm doing some view logic below, you need to change that
        if batch is not None:
            job_inf.batch = batch.id
            job_inf.batchurl = reverse('markup_batch', args=[job_inf.batch, 1])
            job_inf.output_pic_count = batch.num_groups
            job_inf.pic_thumbs = generate_pic_thumbs(batch)

        job_infos.append(job_inf)

    return job_infos



#get and fill up possible actions based on the status of this job
def generate_skaa_actions(job, request):
    ret = []

    #boring always created actions for populating below
    contact = DynamicAction('Contact Doctor', reverse('contact', args=[job.id]), True)

    #TODO remove pie, this is for fun and testing
    #i_like_pie = DynamicAction('I like Pie', 'i_like_pie')
    #u_like_pie = DynamicAction('Do You like Pie', '/u_like_pie')
    #ret.append(i_like_pie)
    #ret.append(u_like_pie)
    #TODO is doctor?
    view_job_url= reverse('markup_batch', args=[job.batch.id, 1])
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
        ret.append(contact)
        ret.append(DynamicAction('Reject', '/reject_doctors_work/'))
        ret.append(DynamicAction('Request Modification', '/request_fix/'))
        ret.append(view_job)
    elif job.status == Job.USER_ACCEPTED:
        ret.append(view_job)
        pass
    elif job.status == Job.USER_REQUESTS_MODIFICATION:
        pass
    elif job.status == Job.USER_REJECTED:
        pass
    else:
        #How did we get here???
        pass

    return ret

def generate_pic_thumbs(filter_batch):
    """
    Get all the pic thumbnails associated with a batch

    Returns an array of tuples like this:
        (thumb_url, markup_url)
    """
    ret = []
    pics = Pic.objects.filter(batch=filter_batch)
    for pic in pics:
        markup_url= reverse('markup_batch', args=[filter_batch.id, pic.group.sequence])
        tup = (pic.get_thumb_url(), markup_url)
        ret.append(tup)
    return ret
        
def create_job(request, batch, price_in_cents):
    j = None
    price = price_in_cents/100
    if batch is not None:
        j = Job(skaa=request.user.get_profile(),
                batch=batch, 
                price = price, 
                status=Job.USER_SUBMITTED)
        j.save()       
        set_groups_locks(batch, True)
    return j

def set_groups_locks(batch_to_lock, state):
    groups = Group.objects.filter(batch=batch_to_lock)
    #Performance Opportunity, just update all at once
    for group in groups:
        group.is_locked = state
        group.save()

@login_required
def accept_doctors_work(request):
    profile = get_profile_or_None(request)
    data = simplejson.loads(request.body)
    job = get_object_or_None(Job, id=data['job_id'])

    result = {"actions": [{"action":"alert","data":"There was an error processing your request."} ]}
    if job and profile and job.skaa == profile:
        #TODO Put money into Doctors account 
        result = {"actions": [{"action":"alert","data":"Bling, bling, Dear Doctor, the Job was accepted!!."},
                              {"action":"reload","data":""}  ]}
        job.status = Job.USER_ACCEPTED
        job.save()

    response_data = simplejson.dumps(result)
    return HttpResponse(response_data, mimetype='application/json')


@login_required
def reject_doctors_work(request):
    profile = get_profile_or_None(request)
    data = simplejson.loads(request.body)
    job = get_object_or_None(Job, id=data['job_id'])

    result = {"actions": [{"action":"alert","data":"There was an error processing your request."} ]}
    if job and profile and job.skaa == profile:
        #TODO Put money into Doctors account 
        result = {"actions": [{"action":"alert","data":"Bling, bling, Dear Doctor, the Job was rejected!!."},
                              {"action":"reload","data":""}  ]}
        job.status = Job.USER_REJECTED
        job.save()

    response_data = simplejson.dumps(result)
    return HttpResponse(response_data, mimetype='application/json')




