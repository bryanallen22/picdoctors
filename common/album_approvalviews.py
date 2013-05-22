from annoying.decorators import render_to
from annoying.functions import get_object_or_None
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.utils import simplejson
from common.models import Job
from common.models import Album
from common.models import Group
from common.models import Pic
from common.functions import get_profile_or_None
from common.calculations import calculate_job_payout
from decimal import *

from common.jobs import get_job_infos_json, get_pagination_info, JobInfo
from common.jobs import Actions, Action, RedirectData, DynamicAction
from common.jobs import fill_job_info
from common.decorators import require_login_as

import math
import ipdb


@require_login_as(['skaa', 'doctor'])
@render_to('jobs.html')
def album_approval_page(request, page=1):
    if not request.user.has_common_perm('album_approver'):
        return redirect('/')

    jobs = Job.objects.filter(status=Job.MODERATOR_APPROVAL_NEEDED).order_by('created').reverse()

    pager, cur_page = get_pagination_info(jobs, page)    

    job_infos_json = get_job_infos_json(cur_page, generate_album_approval_actions, request)

    return {'job_infos_json':job_infos_json,
            'num_pages': range(1,pager.num_pages+1), 'cur_page': int(page), 
            'reverser': 'album_approval_page_with_page', 'doc_page':False, 'title':'Jobs Needing Approval'}

#get and fill up possible actions based on the status of this job
def generate_album_approval_actions(job):
    ret = []
    view_album = DynamicAction('View Album', reverse('album', args=[job.album.id]), True)
    ret.append(view_album)
    return ret
        
