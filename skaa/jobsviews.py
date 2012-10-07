from annoying.decorators import render_to
from annoying.functions import get_object_or_None
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from common.models import Job
from common.models import Batch
from common.models import Group
from common.models import UserProfile
from common.models import Pic
from common.calculations import calculate_job_payout
from django.contrib.auth.models import User
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
        job_inf.status = job.get_job_status_display()
        job_inf.doctor_exists = job.doctor is not None
        batch = job.skaa_batch
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
    contact = DynamicAction('Contact Doctor', 'contact_job_url')

    #TODO remove pie, this is for fun and testing
    #i_like_pie = DynamicAction('I like Pie', 'i_like_pie')
    #u_like_pie = DynamicAction('Do You like Pie', '/u_like_pie')
    #ret.append(i_like_pie)
    #ret.append(u_like_pie)
    #TODO is doctor?
    is_doctor = request.user.get_profile().is_doctor # request.user.get_profile().is cool doctor  ???
    view_job_url= reverse('markup_batch', args=[job.skaa_batch.id, 1])
    view_job = DynamicAction('View Job', view_job_url, True)
    
    if job.job_status == Job.USER_SUBMITTED and is_doctor:
        ret.append(DynamicAction('Apply for Job', '/apply_for_job'))
        ret.append(DynamicAction('Job price too Low', '/job_price_too_low'))
        ret.append(view_job)
    elif job.job_status == Job.TOO_LOW:
        #Do something
        pass
    elif job.job_status == Job.DOCTOR_ACCEPTED:
        ret.append(contact)
        ret.append(view_job)
        #do something
    elif job.job_status == Job.DOCTOR_REQUESTS_ADDITIONAL_INFORMATION:
        ret.append(contact)
        ret.append(view_job)
        #do something
    elif job.job_status == Job.DOCTOR_SUBMITTED:
        ret.append(DynamicAction('Accept', 'accept_job_url'))
        #to be honest I'm not sure how this one will work (at least from this page)
        ret.append(contact)
        ret.append(DynamicAction('Reject', 'reject_job_url'))
        ret.append(view_job)
    elif job.job_status == Job.USER_ACCEPTED:
        #do nothing these are for doctor
        ret.append(view_job)
        pass
    elif job.job_status == Job.USER_REQUESTS_ADDITIONAL_WORK:
        #do nothing these are for doctor
        pass
    elif job.job_status == Job.USER_REJECTS:
        #do nothing these are fordoctor
        pass
    else:
        #How did we get here???
        pass

    return ret

#TODO make sure you aren't offended by the idea of doing all of the pics, maybe down to top 3?
#get all the pic thumbnails associated with a batch (we might drop this down to top 3 or something)
def generate_pic_thumbs(filter_batch):
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
                skaa_batch=batch, 
                price = price, 
                job_status=Job.USER_SUBMITTED)
        j.save()       
        set_groups_locks(batch, True)
    return j

def set_groups_locks(batch_to_lock, state):
    groups = Group.objects.filter(batch=batch_to_lock)
    #Performance Opportunity, just update all at once
    for group in groups:
        group.is_locked = state
        group.save()


