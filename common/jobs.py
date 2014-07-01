from django.core.paginator import Paginator
from django.core.urlresolvers import reverse
from django.utils import simplejson

from common.models import Pic, Job
from common.calculations import calculate_job_payout
from messaging.models import GroupMessage
from common.emberurls import get_ember_url

import ipdb
from copy import deepcopy

from notifications.functions import notify
from notifications.models import Notification

# info for a job row
class JobInfo:
    def __init__(self):
        self.job_id = '1'
        self.output_pic_count = ''
        self.status = 'Unknown'
        self.album = -1
        self.albumurl = ''
        self.pic_thumbs = []
        self.dynamic_actions = []

        #doctor specific
        self.doctor_payout = ''
        self.job_worth = ''
        self.show_links = False

# dictify everything for jsoning
    def to_dict(self):
        dup = deepcopy(self)
        arr = []
        for da in dup.dynamic_actions:
            arr.append(da.__dict__)
        dup.dynamic_actions = arr
        return dup.__dict__

# used for generating the actions on the job row
class DynamicAction:
    def __init__(self, text = '', url = '', redir=False):
        self.text = text
        self.url = url
        self.redir = redir

# Used for responding to the dynamic actions
class Actions:
    def __init__(self):
        self.actions = []
        self.job_info = None

    def add(self, action, data):
        a = Action(action, data)
        self.actions.append(a.__dict__)

    def addJobInfo(self, job_info):
        self.job_info = job_info.to_dict()


    def append(self, item):
        self.actions.append(item.__dict__)

    def clear(self):
        self.actions = []

    def to_json(self):
        return simplejson.dumps(self.__dict__)

# single actions (response to dynamic actions)
class Action:
    def __init__(self, action, data):
        self.action = action
        if hasattr(data, '__dict__'):
            self.data = data.__dict__
        else:
            self.data = data

# special data for the Action class
class RedirectData:
    def __init__(self, href, text):
        self.href = href
        self.text = text

# special data for the Action class
class AlertData:
    def __init__(self, text, alert_class):
        self.text = text
        self.alert_class = alert_class

#I should do error checking
def get_pagination_info(jobs, page):
    #this should be configurable! they maybe want to see 20 jobs...
    pager = Paginator(jobs, 5)

    cur_page = pager.page(page)

    return pager, cur_page

#Populate job info based on job objects from database.
#job infos are a mixture of Pic, Job, & Album
def get_job_infos_json(cur_page_jobs, action_generator, request):
    job_infos = []

    if cur_page_jobs is None:
        return job_infos

    # assume this exists, if it doesn't, they shouldn't be here, crash, i don't care
    profile = request.user
    for job in cur_page_jobs:
        job_inf = fill_job_info(job, action_generator, profile)

        job_infos.append(job_inf.to_dict())

    return simplejson.dumps(job_infos)

def fill_job_info(job, action_generator, profile):
    job_inf = JobInfo()
    job_inf.job_id = job.id
    job_inf.status = job.get_status_display()
    album = job.album
    job_inf.dynamic_actions = action_generator(job)

    job_inf.job_worth = job.stripe_cents

    if job.doctor:
        #pull price from what we promised them
        job_inf.doctor_payout = job.payout_price_cents
    else:
        job_inf.doctor_payout = calculate_job_payout(job, profile)

    job_complete = job.status == Job.USER_ACCEPTED

    # album better exist!
    if album is not None:
        job_inf.album = album.id
        if job_complete:
            job_inf.albumurl = reverse('album', args=[album.id])
        else:
            job_inf.albumurl = get_ember_url('album_markupview', album_id=str(job_inf.album))

        job_inf.output_pic_count = album.num_groups
        job_inf.pic_thumbs = generate_pic_thumbs(album, job_complete)
        job_inf.show_links = album.allow_publicly

    # honestly the job.skaa part is pointless, the template for the user doesn't care about the show_links
    job_inf.show_links = job_inf.show_links or job.status != Job.USER_ACCEPTED or job.skaa == profile

    return job_inf

def generate_pic_thumbs(filter_album, job_complete):
    """
    Get all the pic thumbnails associated with a album

    Returns an array of tuples like this:
        (thumb_url, markup_url)
    """
    ret = []
    pics = Pic.objects.filter(album=filter_album)
    for pic in pics:
        markup_url = ''
        if job_complete:
            markup_url = reverse('album', args=[filter_album.id])
        else:
            markup_url = get_ember_url('album_view', album_id=str(filter_album.id), group_id=str(pic.group.id))

        tup = (pic.get_thumb_url(), markup_url)
        ret.append(tup)
    return ret


def send_job_status_change(request, job, triggered_by):
    send_to = None
    site_path = ''
    doc_path = reverse('doc_job_page_with_page_and_id', args=[1, job.id])
    user_path = reverse('job_page_with_page_and_id', args=[1, job.id])

    # make sure we aren't comparing None to None
    if job.doctor and triggered_by == job.doctor:
        send_to = job.skaa
        site_path = user_path
    elif triggered_by == job.skaa:
        send_to = job.doctor
        site_path = doc_path
    else: # triggered by neither, so send to both?
        if job.doctor:
            #pretend triggered by skaa ;) and send
            send_job_status_change(request, job, job.skaa)
        send_to = job.skaa
        site_path = user_path

    # there is a possibility the doctor doesn't exist
    if not send_to:
        return

    job_no = str(job.id).rjust(8, '0')
    subject = 'Job #' + job_no + ' status has changed to ' + job.get_status_display()
    notify(request=request,
            notification_type=Notification.JOB_STATUS_CHANGE,
            description=subject,
            recipients=send_to,
            url=site_path,
            job=job,
            email_args={})

