from annoying.decorators import render_to
from annoying.functions import get_object_or_None
from django.http import HttpResponse
from django.utils import simplejson
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from common.models import Job 
from common.models import Batch
from common.models import Group
from common.models import UserProfile
from common.models import Pic
from common.calculations import calculate_job_payout
from common.functions import get_profile_or_None
import pdb

from skaa.jobsviews import get_job_infos, get_pagination_info, JobInfo, DynamicAction


#TODO @permissions required to be here...
@login_required
@render_to('doctor_jobs.html')
def doc_job_page(request, page=1):
    jobs = None
    if request.user.is_authenticated():
#        new_jobs = Job.objects.filter(doctor=None)
        doc_jobs = Job.objects.filter(doctor=request.user.get_profile())
        jobs = doc_jobs
    else:
        #TODO they shouldn't ever get here based on future permissions
        jobs = []

    page_info = get_pagination_info(jobs, page)    
    pager = page_info['pager']
    cur_page = page_info['cur_page']


    job_infos = get_job_infos(cur_page, generate_doctor_actions, request)

    return { 'job_infos' :job_infos , 'num_pages': range(1,pager.num_pages+1), 'cur_page': page, 'new_jobs_page': False}


#TODO @permissions required to be here...
@login_required
@render_to('doctor_jobs.html')
def new_job_page(request, page=1):
    #TODO implement paging
    jobs = None
    if request.user.is_authenticated():
        jobs = Job.objects.filter(doctor__isnull=True)
    else:
        #TODO they shouldn't ever get here based on future permissions
        jobs = []

    #TODO fill in paging instead of 1
    page_info = get_pagination_info(jobs, page)    
    pager = page_info['pager']
    cur_page = page_info['cur_page']

    job_infos = get_job_infos(cur_page, generate_doctor_actions, request)

    return { 'job_infos' :job_infos , 'num_pages': range(1,pager.num_pages+1), 'cur_page': page, 'new_jobs_page': True}

#get and fill up possible actions based on the status of this job
def generate_doctor_actions(job, request):
    ret = []
    redirect_url = True
    #boring always created actions for populating below
    #TODO redirect to contact page
    contact = DynamicAction('Contact User', '/', True)
    work_job_url= reverse('markup_batch', args=[job.skaa_batch.id, 1])
    work_job = DynamicAction('Work On Job', work_job_url, redirect_url)

    complete_job = DynamicAction('Mark as Completed', '/mark_job_completed/')
    
    if job.status == Job.USER_SUBMITTED:
        ret.append(DynamicAction('Apply for Job', '/apply_for_job/'))
        ret.append(DynamicAction('Job price too Low', '/job_price_too_low/'))
    elif job.status == Job.TOO_LOW:
        #Doctor won't be informed that a job appears too low
        pass
    elif job.status == Job.DOCTOR_ACCEPTED:
        ret.append(work_job)
        ret.append(complete_job)
        ret.append(contact)
        #do something
    elif job.status == Job.DOCTOR_REQUESTS_ADDITIONAL_INFORMATION:
        ret.append(work_job)
        ret.append(complete_job)
        ret.append(contact)
        #do something
    elif job.status == Job.DOCTOR_SUBMITTED:
        ret.append(contact)
    elif job.status == Job.USER_ACCEPTED:
        #do nothing these are for doctor
        pass
    elif job.status == Job.USER_REQUESTS_MODIFICATION:
        ret.append(work_job)
        ret.append(complete_job)
        ret.append(contact)
        #do nothing these are for doctor
        pass
    elif job.status == Job.USER_REJECTED:
        #do nothing these are fordoctor
        pass
    else:
        #How did we get here???
        pass

    return ret

@login_required
def apply_for_job(request):
    data = simplejson.loads(request.body)
    job = get_object_or_None(Job, id=data['job_id'])
    result = []
    doc = request.user.get_profile()

    #TODO create cool actions, alert, reload, redirect, remove_job_row
    result = {"actions": [{"action":"alert","data":"This job is no longer available"},
                          {"action":"remove_job","data":data['job_id']},
                          {"action":"delay_redirect","data":{"href":reverse("new_job_page"),"view":"available jobs"}}
                         ]}
    if job is None or job.doctor is not None or doc is None:
        #result = ['actions': {'alert':'This job is no longer available', 'reload':''}]
        pass 
    else:
        job_qs = Job.objects.select_for_update().filter(pk=job.id)
        for job in job_qs:
            if job.doctor is None:
                job.doctor = doc
                job.payout_price = calculate_job_payout(job, doc)
                job.status = Job.DOCTOR_ACCEPTED
                job.save()
                result = {"actions": [{"action":"alert","data":"Congrats the job is yours!"},
                                      {"action":"remove_job","data":data['job_id']},
                                      {"action":"delay_redirect","data":{"href":reverse("doc_job_page"),"view": "your jobs"}}
                    ]}

    response_data = simplejson.dumps(result)
    return HttpResponse(response_data, mimetype='application/json')

def has_rights_to_act(profile, job):
    if profile and job:
        if profile == job.doctor:
            return True

    return False

#TODO THIS is bad, it would let the same doctor complain over and over... 
@login_required
def job_price_too_low(request):
    data = simplejson.loads(request.body)
    job = get_object_or_None(Job, id=data['job_id'])
    result = []
    doc = get_profile_or_None(request)

    result = {"actions": [{"action":"alert","data":"There was an error processing your request."} ]}
    if job and not job.doctor:
        job_qs = Job.objects.select_for_update().filter(pk=job.id)
        for job in job_qs:
            job.price_too_low_count += 1
            job.save()
        result = {"actions": [{"action":"alert","data":"Thank you for your input."} ]}

    response_data = simplejson.dumps(result)
    return HttpResponse(response_data, mimetype='application/json')


@login_required
def mark_job_completed(request):
    profile = get_profile_or_None(request)
    data = simplejson.loads(request.body)
    job = get_object_or_None(Job, id=data['job_id'])

    result = {"actions": [{"action":"alert","data":"There was an error processing your request."} ]}
    if has_rights_to_act(profile, job):
        #TODO Check to see if there is an image for every group, email user
        result = {"actions": [{"action":"alert","data":"Bling, bling, Dear User, your Job is complete!!."} ]}
        job.status = Job.DOCTOR_SUBMITTED
        job.save()

    response_data = simplejson.dumps(result)
    return HttpResponse(response_data, mimetype='application/json')



