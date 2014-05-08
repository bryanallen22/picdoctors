from annoying.decorators import render_to
from annoying.functions import get_object_or_None
from django.http import HttpResponse
from django.utils import simplejson
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from common.models import Job
from common.models import Album
from common.models import Group
from common.models import Pic
from common.models import DocBlock
from common.models import PriceTooLowContributor
from common.calculations import calculate_job_payout
from common.functions import get_profile_or_None, get_datetime
from skaa.rejectviews import remove_previous_doctor

from common.jobs import get_job_infos_json, get_pagination_info, JobInfo
from common.jobs import Actions, Action, RedirectData, AlertData, DynamicAction
from common.jobs import send_job_status_change, fill_job_info
from common.decorators import require_login_as
from common.emberurls import get_ember_url
from datetime import timedelta
import datetime
from django.utils.timezone import utc
import ipdb

@require_login_as(['doctor'])
@render_to('jobs.html')
def doc_job_page(request, page=1, job_id=None):
    jobs = None
    profile = get_profile_or_None(request)
    if profile and profile.isa('doctor'):
        if job_id:
            jobs = Job.objects.filter(doctor=profile).filter(id=job_id).order_by('created').reverse()
        else:
            jobs = Job.objects.filter(doctor=profile).order_by('created').reverse()
    else:
        return redirect('/')

    pager, cur_page = get_pagination_info(jobs, page)

    job_infos_json = get_job_infos_json(cur_page, generate_doctor_actions, request)

    return {
            'job_infos_json'   : job_infos_json,
            'num_pages'        : range(1,pager.num_pages+1),
            'cur_page'         : page,
            'reverser'         : 'doc_job_page_with_page',
            'doc_page'         : True,
            'title'            : 'Jobs To Do'
    }


@require_login_as(['doctor'])
@render_to('jobs.html')
def new_job_page(request, page=1):
    jobs = None
    profile = get_profile_or_None(request)
    if profile and profile.isa('doctor'):
        if not profile.can_view_jobs(request, profile):
            if not profile.is_merchant():
                return redirect( reverse('account_settings') + '#merchant_tab' )
            elif not profile.has_bank_account():
                return redirect( reverse('account_settings') + '#bank_tab' )
            else:
                # I don't know how we got here, there is only 2 reasons why
                # they can't view a job, so why else would we reject them?
                return redirect('/')
        # only show jobs where a hold has been placed in the last 6 days 23 hours
        # (hold only lasts 7 days)
        # if a job hasn't been taken in 7 days inform user to up the price!
        now =  get_datetime()
        seven_days_ago = now - timedelta(days=6, hours=23)

        jobs = Job.objects.filter(doctor__isnull=True).exclude(ignore_last_doctor=profile).filter(bp_hold__created__gte=seven_days_ago)
    else:
        return redirect( reverse('permission_denied') )

    pager, cur_page = get_pagination_info(jobs, page)

    job_infos_json = get_job_infos_json(cur_page, generate_doctor_actions, request)

    return {
            'job_infos_json'   : job_infos_json,
            'num_pages'        : range(1,pager.num_pages+1),
            'cur_page'         : page,
            'reverser'         : 'new_job_page_with_page',
            'doc_page'         : True,
            'title'            : 'Available Jobs'
    }

#get and fill up possible actions based on the status of this job
def generate_doctor_actions(job):
    ret = []
    redirect_url = True

    # boring actions used by multiple cases belowg below

    group = job.get_first_unfinished_group()
    group_seq = 1 if not group else group.sequence
    work_job_url = get_ember_url('album_markupview', album_id=str(job.album.id))
    work_job = DynamicAction('Work on Job', work_job_url, redirect_url)

    mark_as_completed = DynamicAction('Mark as Completed', '/mark_job_completed/')

    view_markup_url = get_ember_url('album_markupview', album_id=str(job.album.id))
    view_markup = DynamicAction('View Job', view_markup_url, True)
    view_album = DynamicAction('Before & After Album', reverse('album', args=[job.album.id]), True)
    job_price_too_low = DynamicAction('Job Price Too Low', reverse('job_price_too_low', args=[job.id]), True)
    quit_job = DynamicAction('Return Job To Market', reverse('quit_job', args=[job.id]), True)


    if job.status == Job.IN_MARKET:
        ret.append(view_markup)
        ret.append(DynamicAction('Apply for Job', '/apply_for_job/'))
        ret.append(job_price_too_low)

    elif job.status == Job.DOCTOR_ACCEPTED:
        ret.append(work_job)
        ret.append(view_album)
        ret.append(mark_as_completed)
        ret.append(quit_job)

    elif job.status == Job.MODERATOR_APPROVAL_NEEDED:
        ret.append(view_album)
        ret.append(quit_job)

    elif job.status == Job.DOCTOR_SUBMITTED:
        ret.append(view_album)
        ret.append(quit_job)

    elif job.status == Job.USER_ACCEPTED:
        #do nothing these are for doctor
        pass

    else:
        #How did we get here???
        pass

    return ret

@require_login_as(['doctor'])
def apply_for_job(request):
    job_id = request.POST['job_id']
    job = get_object_or_None(Job, id=job_id)
    profile = get_profile_or_None(request)
    result = []

    actions = Actions()
    actions.add('alert', AlertData('This job is no longer available', 'error'))
    actions.add('remove_job_row', job_id)
    r = RedirectData(reverse("new_job_page"), 'available jobs')
    actions.add('action_button', r)

    if job is None or job.doctor is not None or profile is None:
        pass
    else:
        # Get exclusive access to the job
        job_qs = Job.objects.select_for_update().filter(pk=job.id)
        for job in job_qs:
            # if the job has no doctor
            if job.doctor is None:
                # find out if this job has had this doctor before
                db_cnt = DocBlock.objects.filter(job=job).filter(doctor=profile).count()
                if db_cnt > 0:
                    actions = Actions()
                    actions.add('alert', AlertData('Unfortunately you are unable to take this job, we apologize.', 'error'))
                    actions.add('remove_job_row', job_id)
                    r = RedirectData(reverse("doc_job_page"), 'Go to your jobs')
                    actions.add('action_button', r)
                else:
                    # Update Job Info
                    job.doctor = profile
                    job.approved = profile.auto_approve
                    job.payout_price_cents = calculate_job_payout(job, profile)
                    job.status = Job.DOCTOR_ACCEPTED
                    job.save()

                    # Email
                    send_job_status_change(request, job, profile)

                    # Response
                    actions = Actions()
                    actions.add('alert', AlertData('Congratulations, the job is yours!', 'success'))

                    job_inf = fill_job_info(job, generate_doctor_actions, profile)
                    actions.addJobInfo(job_inf)

                    db = DocBlock(job=job, doctor=profile)
                    db.save()

    return HttpResponse(actions.to_json(), mimetype='application/json')

def has_rights_to_act(profile, job):
    if profile and job:
        if profile == job.doctor:
            return True

    return False


@require_login_as(['doctor'])
def mark_job_completed(request):
    profile = get_profile_or_None(request)
    #data = simplejson.loads(request.body)
    job_id = request.POST['job_id']
    job = get_object_or_None(Job, id=job_id)

    actions = Actions()
    actions.add('alert', AlertData('There was an error processing your request.', 'error'))
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
            actions.add('alert', AlertData('The job has been marked as complete', 'success'))

            # elitest doctor is auto approved, skip to submitted state!
            if profile.auto_approve:
                job.status = Job.DOCTOR_SUBMITTED
            else:
                job.status = Job.MODERATOR_APPROVAL_NEEDED

            job.save()
            send_job_status_change(request, job, profile)
            job_info = fill_job_info(job, generate_doctor_actions, profile)
            actions.addJobInfo(job_info)
        else:
            plural = unfinished_count > 1
            plural_to_be = 'are' if plural else 'is'
            plural_s = 's' if plural else ''
            actions.add('alert', AlertData(str(unfinished_count) + ' group' + plural_s + ' ' + plural_to_be + ' missing a doctored picture.', 'error'))
            redir_url = get_ember_url('album_view', album_id=job.album.id, group_id=missing_group.id)
            r =  RedirectData(redir_url,'Go to the first missing picture')
            actions.add('action_button', r)
    return HttpResponse(actions.to_json(), mimetype='application/json')

@require_login_as(['doctor'])
@render_to("quit_job.html")
def quit_job(request, job_id):

    profile = get_profile_or_None(request)
    job = get_object_or_None(Job, id=job_id)

    if not profile == job.doctor:
        return redirect( reverse('permission_denied') )

    return  {
            'job_id'        : job_id,
            }

@require_login_as(['doctor'])
def quit_job_endpoint(request):
    profile = get_profile_or_None(request)
    data = simplejson.loads(request.body)
    job = get_object_or_None(Job, id=int(data['job_id']))

    if job and job.doctor and job.doctor == profile:
        remove_previous_doctor(job)

    send_job_status_change(request, job, profile)

    result = { 'relocate' : reverse('doc_job_page') }
    response_data = simplejson.dumps(result)
    return HttpResponse(response_data, mimetype='application/json')
