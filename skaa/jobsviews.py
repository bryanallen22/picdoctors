from annoying.decorators import render_to
from annoying.functions import get_object_or_None
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from common.models import Job
from common.models import Batch
from common.models import Group
from common.models import UserProfile
from common.models import Pic
from skaa.uploadviews import get_batch_id
from django.contrib.auth.models import User
import pdb

class JobInfo:
    def __init__(self):
        self.job_id = '1'
        self.batch_info = 'Unknown'
        self.status = 'Unknown'
        self.doctor_exists = False
        self.batch = -1
        self.pic_thumbs = []

@render_to('jobs.html')
def job_page(request):
    #TODO jobs = Job.objects.filter(skaa = whoever's logged in)
    #TODO implement paging
    jobs = Job.objects.all()

    job_infos = []
    for job in jobs:
        job_inf = JobInfo()
        job_inf.job_id = "{0:06d}".format(job.id)
        job_inf.status = job.get_job_status_display()
        job_inf.doctor_exists = job.doctor is not None
        batch = job.skaa_batch
        if batch is not None:
            job_inf.batch = batch.id
            count = batch.num_groups
            plural = ' ' if count == 1 else 's'
            job_inf.batch_info = str(batch.num_groups) + ' output picture' + plural
            job_inf.pic_thumbs = fill_pic_thumbs(batch)

        job_infos.append(job_inf)


    return { 'job_infos' :job_infos}

#get all the pic thumbnails associated with a batch (we might drop this down to top 3 or something)
def fill_pic_thumbs(filter_batch):
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
                    job_status=Job.STATUS_USER_SUBMITTED)
            j.save()       
        else:
            j.deleted = 0
            j.save()
        set_groups_locks(b, True)
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


