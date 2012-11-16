from annoying.decorators import render_to
from annoying.functions import get_object_or_None
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.utils import simplejson
from common.models import Job
from common.models import Album
from common.models import Group
from common.models import UserProfile
from common.models import Pic
from common.models import Charge
from common.functions import get_profile_or_None
from common.calculations import calculate_job_payout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from decimal import *

from common.jobs import get_job_infos_json, get_pagination_info, JobInfo
from common.jobs import Actions, Action, RedirectData, DynamicAction
from common.jobs import send_job_status_change, fill_job_info

import math
import pdb


@login_required
@render_to('jobs.html')
def album_approval_page(request, page=1):
    if request.user.is_authenticated():
        jobs = Job.objects.filter(approved=False).order_by('created').reverse()
    else:
        #TODO they shouldn't ever get here based on future permissions
        jobs = []

    pager, cur_page = get_pagination_info(jobs, page)    

    job_infos_json = get_job_infos_json(cur_page, generate_album_approval_actions, request)

    return {'job_infos_json':job_infos_json,
            'num_pages': range(1,pager.num_pages+1), 'cur_page': int(page), 
            'doc_page':False}

#get and fill up possible actions based on the status of this job
def generate_album_approval_actions(job):
    ret = []
    view_album = DynamicAction('View Album', reverse('album', args=[job.album.id]), True)
    ret.append(view_album)
    return ret
        
