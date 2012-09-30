from annoying.decorators import render_to
from annoying.functions import get_object_or_None
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.http import HttpResponse
from django.utils import simplejson
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from common.models import Job 
from common.models import Batch
from common.models import Group
from common.models import UserProfile
from common.models import Pic
from common.calculations import calculate_job_payout
import pdb

from skaa.jobsviews import get_job_infos, get_pagination_info, JobInfo, DynamicAction


#TODO @permissions required to be here...
@render_to('doctor_jobs.html')
def doc_job_page(request, page=1):
    #TODO implement paging
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

    #boring always created actions for populating below
    #TODO redirect to contact page
    contact = DynamicAction('Contact User', '/', True)
    complete_job_url= reverse('markup_batch', args=[job.skaa_batch.id, 1])
    complete_job = DynamicAction('Complete Job', complete_job_url, True)
    
    if job.job_status == Job.USER_SUBMITTED:
        ret.append(DynamicAction('Apply for Job', '/apply_for_job'))
        ret.append(DynamicAction('Job price too Low', '/job_price_too_low'))
    elif job.job_status == Job.TOO_LOW:
        #Doctor won't be informed that a job appears too low
        pass
    elif job.job_status == Job.DOCTOR_ACCEPTED:
        ret.append(complete_job)
        ret.append(contact)
        #do something
    elif job.job_status == Job.DOCTOR_REQUESTS_ADDITIONAL_INFORMATION:
        ret.append(complete_job)
        ret.append(contact)
        #do something
    elif job.job_status == Job.DOCTOR_SUBMITTED:
        ret.append(DynamicAction('Accept', 'accept_job_url'))
        ret.append(contact)
        ret.append(DynamicAction('Reject', 'reject_job_url'))
    elif job.job_status == Job.USER_ACCEPTED:
        #do nothing these are for doctor
        pass
    elif job.job_status == Job.USER_REQUESTS_ADDITIONAL_WORK:
        ret.append(complete_job)
        #do nothing these are for doctor
        pass
    elif job.job_status == Job.USER_REJECTS:
        #do nothing these are fordoctor
        pass
    else:
        #How did we get here???
        pass

    return ret
@csrf_protect
def apply_for_job(request):
    data = simplejson.loads(request.body)
    job = get_object_or_None(Job, id=data['job_id'])
    result = []
    doc = request.user.get_profile()

    #TODO create cool actions, alert, reload, redirect, remove_job_row
    result = {"actions": [{"action":"alert","data":"This job is no longer available"},
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
                job.job_status = Job.DOCTOR_ACCEPTED
                job.save()
                result = {"actions": 
                        [{"action":"alert","data":"Congrats the job is yours!"},
                    {"action":"delay_redirect","data":{"href":reverse("doc_job_page"),"view": "your jobs"}}
                    ]}


    #TODO remove this
    response_data = simplejson.dumps(result)
    return HttpResponse(response_data, mimetype='application/json')
