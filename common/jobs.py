from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.paginator import Paginator
from django.core.urlresolvers import reverse
from django.utils import simplejson

from common.models import Pic
from common.calculations import calculate_job_payout
from tasks.tasks import sendAsyncEmail

# info for a job row
class JobInfo:
    def __init__(self):
        self.job_id = '1'
        self.output_pic_count = ''
        self.status = 'Unknown'
        self.doctor_exists = False
        self.batch = -1
        self.batchurl = ''
        self.pic_thumbs = []
        self.dynamic_actions = []

        #doctor specific
        self.doctor_payout = ''

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

    def add(self, action, data):
        a = Action(action, data)
        self.actions.append(a.__dict__)

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

    return {'pager': pager, 'cur_page':cur_page }

#Populate job info based on job objects from database.
#job infos are a mixture of Pic, Job, & Batch
def get_job_infos(cur_page_jobs, action_generator, request):
    job_infos = []

    if cur_page_jobs is None:
        return job_infos

    for job in cur_page_jobs:
        job_inf = JobInfo()
        job_inf.job_id = job.id
        job_inf.status = job.get_status_display()
        job_inf.doctor_exists = job.doctor is not None
        batch = job.batch
        job_inf.dynamic_actions = action_generator(job, request)

        if job_inf.doctor_exists:
            #pull price from what we promised them
            job_inf.doctor_payout = job.payout_price
        else:
            job_inf.doctor_payout = calculate_job_payout(job, request.user.get_profile())

        #TODO I'm doing some view logic below, you need to change that
        if batch is not None:
            job_inf.batch = batch.id
            job_inf.batchurl = reverse('markup_batch', args=[job_inf.batch, 1])
            job_inf.output_pic_count = batch.num_groups
            job_inf.pic_thumbs = generate_pic_thumbs(batch)

        job_infos.append(job_inf)

    return job_infos

def generate_pic_thumbs(filter_batch):
    """
    Get all the pic thumbnails associated with a batch

    Returns an array of tuples like this:
        (thumb_url, markup_url)
    """
    ret = []
    pics = Pic.objects.filter(batch=filter_batch)
    for pic in pics:
        markup_url= reverse('markup_batch', args=[filter_batch.id, pic.group.sequence])
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
        sendAsyncEmail.apply_async(args=[msg])

    except Exception as ex:
        #later I'd like to ignore this, but for now, let's see errors happen
        raise ex

