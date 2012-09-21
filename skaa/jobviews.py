from annoying.decorators import render_to
from annoying.functions import get_object_or_None
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from common.models import Job
from common.models import Batch
from common.models import Group
from common.models import UserProfile
from skaa.uploadviews import get_batch_id
from django.contrib.auth.models import User
import pdb

class JobInfo:
    def __init__(self):
        self.job_id = '1'
        self.batch_info = 'Unknown'
        self.status = 'Unknown'
        self.doctor_exists = False

@render_to('job.html')
def index(request):
    #TODO jobs = Job.objects.filter(skaa = whoever's logged in)
    #TODO implement paging
    jobs = Job.objects.all()

    job_infos = []
    for job in jobs:
        job_inf = JobInfo()
        job_inf.job_id = "{0:09d}".format(job.id)
        job_inf.status = job.get_job_status_display()
        job_inf.doctor_exists = job.doctor is not None
        batch = job.skaa_batch
        if batch is not None:
            count = batch.num_groups
            plural = ' ' if count == 1 else 's'
            job_inf.batch_info = str(batch.num_groups) + ' output picture' + plural
        job_infos.append(job_inf)


    return { 'job_infos' :job_infos}

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
            j = Job(skaa_batch=b, 
                    price = 99.99, 
                    job_status=Job.STATUS_USER_SUBMITTED)
            j.save()       

            lock_groups(b)
    except Exception as e:
        return HttpResponse('{ "success" : true; "whynot" :"' + str(e) + '"}', mimetype='application/json')

    return HttpResponse('{ "success" : true }', mimetype='application/json')


def lock_groups(batch_to_lock):
    groups = Group.objects.filter(batch=batch_to_lock)
    #Performance Opportunity, just update all at once
    for group in groups:
        group.is_locked = True
        group.save()

