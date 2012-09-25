from annoying.decorators import render_to
from annoying.functions import get_object_or_None
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from common.models import Job
from common.models import Batch
from common.models import Group
from common.models import UserProfile
from common.models import Pic
from django.contrib.auth.models import User
import pdb

from skaa.jobsviews import fill_job_infos, JobInfo

class DynamicAction:
    def __init__(self, text = '', url = ''):
        self.text = text
        self.url = url


#TODO @permissions required to be here...
@render_to('doctor_jobs.html')
def doc_job_page(request):
    #TODO implement paging
    jobs = None
    if request.user.is_authenticated():
#        new_jobs = Job.objects.filter(doctor=None)
        doc_jobs = Job.objects.filter(doctor=request.user.get_profile())
        jobs = doc_jobs
    else:
        #TODO they shouldn't ever get here based on future permissions
        jobs = []

    job_infos = fill_job_infos(jobs, request)

    return { 'job_infos' :job_infos }


#TODO @permissions required to be here...
@render_to('doctor_jobs.html')
def new_job_page(request):
    #TODO implement paging
    jobs = None
    if request.user.is_authenticated():
        new_jobs = Job.objects.filter(doctor__isnull=True)
        jobs = new_jobs 
    else:
        #TODO they shouldn't ever get here based on future permissions
        jobs = []

    job_infos = fill_job_infos(jobs, request)

    return { 'job_infos' :job_infos }
