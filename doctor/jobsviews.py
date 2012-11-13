from annoying.decorators import render_to
from annoying.functions import get_object_or_None
from django.http import HttpResponse
from django.utils import simplejson
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from common.models import Job 
from common.models import Album
from common.models import Group
from common.models import UserProfile
from common.models import Pic
from common.calculations import calculate_job_payout
from common.functions import get_profile_or_None

from common.jobs import get_job_infos_json, get_pagination_info, JobInfo 
from common.jobs import Actions, Action, RedirectData, DynamicAction 
from common.jobs import send_job_status_change, fill_job_info
import pdb

@login_required
@render_to('jobs.html')
def doc_job_page(request, page=1):
    jobs = None
    profile = get_profile_or_None(request)
    if profile and profile.is_doctor:
#        new_jobs = Job.objects.filter(doctor=None)
        jobs = Job.objects.filter(doctor=profile).order_by('created').reverse()
    else:
        return redirect('/')

    pager, cur_page = get_pagination_info(jobs, page)    

    job_infos_json = get_job_infos_json(cur_page, generate_doctor_actions, request)

    return { 'job_infos_json' : job_infos_json, 
            'num_pages': range(1,pager.num_pages+1), 'cur_page': page, 
            'new_jobs_page': False, 'doc_page':True}


@login_required
@render_to('jobs.html')
def new_job_page(request, page=1):
    jobs = None
    profile = get_profile_or_None(request)
    if profile and profile.is_doctor:
        jobs = Job.objects.filter(doctor__isnull=True)
    else:
        return redirect('/')

    pager, cur_page = get_pagination_info(jobs, page)    

    job_infos_json = get_job_infos_json(cur_page, generate_doctor_actions, request)

    return {'job_infos_json' : job_infos_json, 
            'num_pages': range(1,pager.num_pages+1), 'cur_page': page, 
            'new_jobs_page': True, 'doc_page':True}

#get and fill up possible actions based on the status of this job
def generate_doctor_actions(job):
    ret = []
    redirect_url = True
    #boring always created actions for populating below
    #TODO redirect to contact page
    contact = DynamicAction('Contact User', reverse('message', args=[job.id]), True)

    group = job.get_first_unfinished_group()
    group_seq = 1 if not group else group.sequence
    work_job_url= reverse('markup_album', args=[job.album.id, group_seq])
    work_job = DynamicAction('Work On Job', work_job_url, redirect_url)

    complete_job = DynamicAction('Mark as Completed', '/mark_job_completed/')
    
    view_markup_url= reverse('markup_album', args=[job.album.id, 1])
    view_markup = DynamicAction('View Job', view_markup_url, True)
    view_album = DynamicAction('View Album', reverse('album', args=[job.album.id]), True)
    

    if job.status == Job.USER_SUBMITTED:
        ret.append(view_markup)
        ret.append(DynamicAction('Apply for Job', '/apply_for_job/'))
        ret.append(DynamicAction('Job price too Low', '/job_price_too_low/'))
    elif job.status == Job.TOO_LOW:
        #Doctor won't be informed that a job appears too low
        pass
    elif job.status == Job.DOCTOR_ACCEPTED:
        ret.append(work_job)
        ret.append(view_album)
        ret.append(complete_job)
        ret.append(contact)
        #do something
    elif job.status == Job.DOCTOR_REQUESTS_ADDITIONAL_INFORMATION:
        ret.append(work_job)
        ret.append(view_album)
        ret.append(complete_job)
        ret.append(contact)
        #do something
    elif job.status == Job.DOCTOR_SUBMITTED:
        ret.append(contact)
        ret.append(view_album)
    elif job.status == Job.USER_ACCEPTED:
        #do nothing these are for doctor
        pass
    elif job.status == Job.USER_REQUESTS_MODIFICATION:
        ret.append(work_job)
        ret.append(view_album)
        ret.append(complete_job)
        ret.append(contact)
        #do nothing these are for doctor
        pass
    elif job.status == Job.USER_REJECTED:
        #do nothing these are fordoctor
        pass
    else:
        #How did we get here???
        pass

    return ret

@login_required
def apply_for_job(request):
    data = simplejson.loads(request.body)
    job = get_object_or_None(Job, id=data['job_id'])
    profile = get_profile_or_None(request)
    result = []
    doc = request.user.get_profile()

    #TODO create cool actions, alert, reload, redirect, remove_job_row
    actions = Actions()
    actions.add('alert', 'This job is no longer available')
    actions.add('remove_job_row', data['job_id'])
    r = RedirectData(reverse("new_job_page"), 'available jobs')
    actions.add('delay_redirect', r)
    
    if job is None or job.doctor is not None or doc is None:
        #result = ['actions': {'alert':'This job is no longer available', 'reload':''}]
        pass 
    else:
        job_qs = Job.objects.select_for_update().filter(pk=job.id)
        for job in job_qs:
            if job.doctor is None:
                job.doctor = doc
                job.payout_price_cents = calculate_job_payout(job, doc)
                job.status = Job.DOCTOR_ACCEPTED
                job.save()
                send_job_status_change(job, profile)
                actions = Actions()
                actions.add('alert', 'Congrats the job is yours!')
                #actions.add('remove_job_row', data['job_id'])
                r = RedirectData(reverse("doc_job_page"), 'your jobs')
                actions.add('delay_redirect', r)
                job_inf = fill_job_info(job, generate_doctor_actions, profile)
                actions.addJobInfo(job_inf)

    return HttpResponse(actions.to_json(), mimetype='application/json')

def has_rights_to_act(profile, job):
    if profile and job:
        if profile == job.doctor:
            return True

    return False

#TODO THIS is bad, it would let the same doctor complain over and over... 
@login_required
def job_price_too_low(request):
    data = simplejson.loads(request.body)
    job = get_object_or_None(Job, id=data['job_id'])
    result = []
    doc = get_profile_or_None(request)
    actions = Actions()
    actions.add('alert', 'There was an error processing your request.')

    if job and not job.doctor:
        job_qs = Job.objects.select_for_update().filter(pk=job.id)
        for job in job_qs:
            job.price_too_low_count += 1
            job.save()
        actions.clear()
        actions.add('alert', 'Thank you for your input.')

    return HttpResponse(actions.to_json(), mimetype='application/json')


@login_required
def mark_job_completed(request):
    profile = get_profile_or_None(request)
    data = simplejson.loads(request.body)
    job = get_object_or_None(Job, id=data['job_id'])

    actions = Actions()
    actions.add('alert', 'There was an error processing your request.')
    if has_rights_to_act(profile, job):
        groups = Group.get_job_groups(job)
        unfinished_count = 0
        missing_group = None
        for group in groups:
            has_pic = group.has_doctor_pic()
            if not has_pic:
                unfinished_count += 1
                # first missing group
                if not missing_group:
                    missing_group = group

        actions.clear()

        if unfinished_count==0:
            actions.add('alert', 'The job has been marked as complete')
            job.status = Job.DOCTOR_SUBMITTED
            job.save()
            send_job_status_change(job, profile)
            job_info = fill_job_info(job, generate_doctor_actions, profile)
            actions.addJobInfo(job_info)
        else:
            plural = unfinished_count > 1
            plural_to_be = 'are' if plural else 'is'
            plural_s = 's' if plural else ''
            actions.add('alert', str(unfinished_count) + ' group' + plural_s + ' ' + plural_to_be + ' missing a doctored picture.')
            redir_url = reverse('markup_album', args=[job.album.id, missing_group.sequence])
            r =  RedirectData(redir_url,'the first missing picture')
            actions.add('delay_redirect', r)
    return HttpResponse(actions.to_json(), mimetype='application/json')

