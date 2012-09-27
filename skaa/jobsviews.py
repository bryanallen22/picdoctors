from annoying.decorators import render_to
from annoying.functions import get_object_or_None
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.http import HttpResponse
from common.models import Job
from common.models import Batch
from common.models import Group
from common.models import UserProfile
from common.models import Pic
import math
from skaa.uploadviews import get_batch_id, set_batch_id
from django.contrib.auth.models import User
from decimal import *
import pdb

class JobInfo:
    def __init__(self):
        self.job_id = '1'
        self.output_pic_count = ''
        self.status = 'Unknown'
        self.doctor_exists = False
        self.batch = -1
        self.pic_thumbs = []
        self.dynamic_actions = []

        #doctor specific
        self.doctor_payout = ''

class DynamicAction:
    def __init__(self, text = '', url = ''):
        self.text = text
        self.url = url


#TODO @permissions required to be here...
@render_to('jobs.html')
def job_page(request):
    #TODO implement paging
    if request.user.is_authenticated():
        jobs = Job.objects.filter(skaa=request.user.get_profile())
    else:
        #TODO they shouldn't ever get here based on future permissions
        jobs = []

    page_info = get_pagination_info(jobs, 1)    
    pager = page_info['pager']
    cur_page = page_info['cur_page']


    job_infos = get_job_infos(cur_page, request)


    return { 'job_infos' :job_infos }

#I should do error checking
def get_pagination_info(jobs, page):
    #this should be configurable! they maybe want to see 20 jobs...
    pager = Paginator(jobs, 5)
    
    cur_page = pager.page(page)

    return {'pager': pager, 'cur_page':cur_page }

#Populate job info based on job objects from database.
#job infos are a mixture of Pic, Job, & Batch
def get_job_infos(cur_page_jobs,  request):
    job_infos = []

    if cur_page_jobs is None:
        return job_infos

    for job in cur_page_jobs:
        job_inf = JobInfo()
        job_inf.job_id = job.id
        job_inf.status = job.get_job_status_display()
        job_inf.doctor_exists = job.doctor is not None
        batch = job.skaa_batch
        job_inf.dynamic_actions = generate_actions(job, request)

        if job_inf.doctor_exists:
            #pull price from what we promised them
            job_inf.doctor_payout = job.payout_price
        else:
            #TODO Find out if current logged in user is doctor, if so, figure out how 
            #valuable they are, and generate a percent for them
            #if request.user.get_profile().is_cool_doctor or stupid
            #chop off extra half penny
            doctors_cut = Decimal(.5)
            job_inf.doctor_payout = math.floor(100 * job.price * doctors_cut) / 100

        #TODO I'm doing some view logic below, you need to change that
        if batch is not None:
            job_inf.batch = batch.id
            job_inf.output_pic_count = batch.num_groups
            job_inf.pic_thumbs = generate_pic_thumbs(batch)

        job_infos.append(job_inf)

    return job_infos



#get and fill up possible actions based on the status of this job
def generate_actions(job, request):
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
    
    if job.job_status == Job.USER_SUBMITTED and is_doctor:
        ret.append(DynamicAction('Apply for Job', 'apply_for_job'))
        ret.append(DynamicAction('Job price too Low', 'job_price_too_low'))
    elif job.job_status == Job.TOO_LOW:
        #Do something
        pass
    elif job.job_status == Job.DOCTOR_ACCEPTED:
        ret.append(contact)
        #do something
    elif job.job_status == Job.DOCTOR_REQUESTS_ADDITIONAL_INFORMATION:
        ret.append(contact)
        #do something
    elif job.job_status == Job.DOCTOR_SUBMITTED:
        ret.append(DynamicAction('Accept', 'accept_job_url'))
        #to be honest I'm not sure how this one will work (at least from this page)
        ret.append(contact)
        ret.append(DynamicAction('Reject', 'reject_job_url'))
    elif job.job_status == Job.USER_ACCEPTED:
        #do nothing these are for doctor
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

#get all the pic thumbnails associated with a batch (we might drop this down to top 3 or something)
def generate_pic_thumbs(filter_batch):
    ret = []
    pics = Pic.objects.filter(batch=filter_batch)
    for pic in pics:
        tup = (pic.get_thumb_url(), pic.group.sequence)
        ret.append(tup)
    return ret
        


#TODO this method won't be a webmethod, it will only be called after a successful payment, but that's not implemented yet...
@csrf_exempt
def generate_job(request):
    batch_id = get_batch_id(request)
    #start building random stuff
    #TODO Get user and real price and store that info as well... 
    try:
        b = get_object_or_None(Batch, id=batch_id)
        j = get_object_or_None(Job, skaa_batch=b)
        if j is None:
            j = Job(skaa=request.user.get_profile(),
                    skaa_batch=b, 
                    price = 99.99, 
                    job_status=Job.USER_SUBMITTED)
            j.save()       
        else:
            j.deleted = 0
            j.save()
        set_groups_locks(b, True)

        #Remove the batch from the user's session, they are no longer working on it
        set_batch_id(request, None)
    except Exception as e:
        return HttpResponse('{ "success" : true; "whynot" :"' + str(e) + '"}', mimetype='application/json')

    return HttpResponse('{ "success" : true }', mimetype='application/json')


#TODO Delete this method, it's only for testing
@csrf_exempt
def kill_job(request):
    batch_id = get_batch_id(request)
    b = get_object_or_None(Batch, id=batch_id)
    j = get_object_or_None(Job, skaa_batch=b)
    if j is not None:
        j.delete()

    set_groups_locks(b, False)
    return HttpResponse('{ "success" : true }', mimetype='application/json')


def set_groups_locks(batch_to_lock, state):
    groups = Group.objects.filter(batch=batch_to_lock)
    #Performance Opportunity, just update all at once
    for group in groups:
        group.is_locked = state
        group.save()


