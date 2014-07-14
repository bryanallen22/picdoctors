from annoying.decorators import render_to
from annoying.functions import get_object_or_None
from django.core.urlresolvers import reverse
from common.models import Job
from common.models import Album
from common.models import Group
from common.models import Pic
from common.models import DocBlock
from common.models import PriceTooLowContributor
from common.calculations import calculate_job_payout
from common.functions import get_profile_or_None, get_datetime, get_all_album_approvers
from skaa.rejectviews import remove_previous_doctor

from common.jobs import get_job_infos_json, get_pagination_info, JobInfo
from common.jobs import Actions, Action, RedirectData, AlertData, DynamicAction
from common.jobs import send_job_status_change, fill_job_info
from common.decorators import require_login_as
from common.emberurls import get_ember_url

import settings
import ipdb
import logging; log = logging.getLogger('pd')


@require_login_as(['admin'])
@render_to('jobs.html')
def admin_job_page(request, page=1):
    jobs = None
    profile = get_profile_or_None(request)
    jobs = Job.objects.order_by('created').reverse()

    pager, cur_page = get_pagination_info(jobs, page)

    job_infos_json = get_job_infos_json(cur_page, generate_admin_actions, request)

    return {
            'job_infos_json'   : job_infos_json,
            'num_pages'        : range(1,pager.num_pages+1),
            'cur_page'         : page,
            'reverser'         : 'admin_job_page',
            'doc_page'         : True,
            'title'            : 'Admin Stuff'
    }

#get and fill up possible actions based on the status of this job
def generate_admin_actions(job):
    ret = []
    redirect_url = True

    # boring actions used by multiple cases belowg below
    view_markup_url = get_ember_url('album_markupview', album_id=str(job.album.id))
    view_markup = DynamicAction('View Job', view_markup_url, True)
    view_album = DynamicAction('Before & After Album', reverse('album', args=[job.album.id]), True)
    job_price_too_low = DynamicAction('Job Price Too Low', reverse('job_price_too_low', args=[job.id]), True)
    quit_job = DynamicAction('Return Job To Market', reverse('quit_job', args=[job.id]), True)

    ret.append(view_markup)
    ret.append(view_album)
    ret.append(quit_job)

    if job.status == Job.IN_MARKET:
        ret.append(job_price_too_low)

    elif job.status == Job.DOCTOR_ACCEPTED:
        pass

    elif job.status == Job.MODERATOR_APPROVAL_NEEDED:
        pass

    elif job.status == Job.DOCTOR_SUBMITTED:
        pass

    elif job.status == Job.USER_ACCEPTED:
        #do nothing these are for doctor
        pass

    else:
        #How did we get here???
        pass

    return ret
