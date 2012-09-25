from annoying.decorators import render_to
from annoying.functions import get_object_or_None
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from common.models import Job
from common.models import Batch
from common.models import Group
from common.models import UserProfile
from common.models import Pic
from skaa.uploadviews import get_batch_id, set_batch_id
from django.contrib.auth.models import User
from decimal import *
import pdb

class JobInfo:
    def __init__(self):
        self.job_id = '1'
        self.batch_info = 'Unknown'
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

    job_infos = fill_job_infos(jobs, request)


    return { 'job_infos' :job_infos }


#Populate job info based on job objects from database.
#job infos are a mixture of Pic, Job, & Batch
def fill_job_infos(jobs, request):
    job_infos = []

    if jobs is None:
        return job_infos

    for job in jobs:
        job_inf = JobInfo()
        job_inf.job_id = job.id
        job_inf.status = job.get_job_status_display()
        job_inf.doctor_exists = job.doctor is not None
        batch = job.skaa_batch
        job_inf.dynamic_actions = generate_actions(job)

        if job_inf.doctor_exists:
            #pull price from what we promised them
            job_inf.doctor_payout = job.payout_price
        else:
            #TODO Find out if current logged in user is doctor, if so, figure out how 
            #valuable they are, and generate a percent for them
            #if request.user.get_profile().is_cool_doctor or stupid
            job_inf.doctor_payout = job.price * Decimal(.5)

        #TODO I'm doing some view logic below, you need to change that
        if batch is not None:
            job_inf.batch = batch.id
            count = batch.num_groups
            plural = ' ' if count == 1 else 's'
            job_inf.batch_info = str(batch.num_groups) + ' output picture' + plural
            job_inf.pic_thumbs = generate_pic_thumbs(batch)

        job_infos.append(job_inf)

    return job_infos



#get and fill up possible actions based on the status of this job
def generate_actions(job):
    ret = []

    waste = 1
    #boring always created actions for populating below
    contact = DynamicAction('Contact Doctor', 'contact_job_url')

    #TODO remove pie, this is for fun and testing
    i_like_pie = DynamicAction('I like Pie', 'i_like_pie')
    u_like_pie = DynamicAction('Do You like Pie', '/u_like_pie')
    ret.append(i_like_pie)
    ret.append(u_like_pie)
    
    if job.job_status == Job.USER_SUBMITTED:
        #No actions available
        waste += 1
    elif job.job_status == Job.TOO_LOW:
        #Do something
        waste += 1
    elif job.job_status == Job.DOCTOR_ACCEPTED:
        ret.append(contact)
        #do something
        waste += 1
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
        waste += 1
    elif job.job_status == Job.USER_REQUESTS_ADDITIONAL_WORK:
        #do nothing these are for doctor
        waste += 1
    elif job.job_status == Job.USER_REJECTS:
        #do nothing these are fordoctor
        waste += 1
    else:
        #How did we get here???
        waste += 1

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


