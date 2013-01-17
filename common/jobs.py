from django.core.paginator import Paginator
from django.core.urlresolvers import reverse
from django.utils import simplejson

from common.models import Pic
from common.calculations import calculate_job_payout
from messaging.models import JobMessage, GroupMessage
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import EmailMultiAlternatives
from tasks.tasks import sendAsyncEmail

import pdb
from copy import deepcopy

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

# TODO remove the dup stuff, I'm just doing it so I don't break the current functionality
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
    def __init__(self, href, view):
        self.href = href
        self.view = view

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
    profile = request.user.get_profile()
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

    job_inf.job_worth = job.bp_hold_wrapper.cents

    if job.doctor:
        #pull price from what we promised them
        job_inf.doctor_payout = job.payout_price_cents
    else:
        job_inf.doctor_payout = calculate_job_payout(job, profile)

    # album better exist!
    if album is not None:
        job_inf.album = album.id
        job_inf.albumurl = reverse('markup_album', args=[job_inf.album, 1])
        job_inf.output_pic_count = album.num_groups
        job_inf.pic_thumbs = generate_pic_thumbs(album)

    return job_inf

def generate_pic_thumbs(filter_album):
    """
    Get all the pic thumbnails associated with a album

    Returns an array of tuples like this:
        (thumb_url, markup_url)
    """
    ret = []
    pics = Pic.objects.filter(album=filter_album)
    for pic in pics:
        markup_url= reverse('markup_album', args=[filter_album.id, pic.group.sequence])
        tup = (pic.get_thumb_url(), markup_url)
        ret.append(tup)
    return ret


def send_job_status_change(job, profile):
    try:
        to_email = ''
        if job.doctor and job.doctor == profile:
            to_email = job.skaa.user.email
        else:
            to_email = job.doctor.user.email

        subject = 'Job #' + str(job.id).rjust(8, '0') + ' status has changed.'

        args = {'job_status':job.get_status_display(), 'job_id':job.id} 
        html_content = render_to_string('job_status_change_email.html', args)
                                        
        
        # this strips the html, so people will have the text
        text_content = strip_tags(html_content) 
        # create the email, and attach the HTML version as well.
        msg = EmailMultiAlternatives(subject, text_content, 'donotreply@picdoctors.com', [to_email])
        msg.attach_alternative(html_content, "text/html")
        #TODO if you want to switch to using the workers
        # sendAsyncEmail.apply_async(args=[msg])
        sendAsyncEmail(msg)

    except Exception as ex:
        # later I'd like to ignore this, but for now, let's see errors happen
        # raise ex
        pass

