from annoying.decorators import render_to
from annoying.functions import get_object_or_None

from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import redirect
from django.utils import simplejson

from common.decorators import require_login_as
from common.functions import get_profile_or_None
from common.models import Job, Pic, Album, Group
from common.jobs import send_job_status_change
from notifications.functions import notify
from notifications.models import Notification

import logging; log = logging.getLogger('pd')

@require_login_as(['skaa'])
@render_to("reject.html")
def refund(request, job_id):

    if not reject_belongs(request, job_id):
        return redirect( reverse('permission_denied') )

    job = get_object_or_None(Job, id=job_id)

    first_group = min([pic.group_id for pic in Pic.objects.filter(album=job.album)])

    return  {
            'job_id'        : job_id,
            'album_id'      : job.album.id,
            'first_group'   : first_group,
            'is_refund'     : True,
            }


@require_login_as(['skaa'])
@render_to("reject.html")
def switch_doctor(request, job_id):

    if not reject_belongs(request, job_id):
        return redirect( reverse('permission_denied') )

    job = get_object_or_None(Job, id=job_id)
    first_group = min([pic.group_id for pic in Pic.objects.filter(album=job.album)])

    return  {
            'job_id'        : job_id,
            'album_id'      : job.album.id,
            'first_group'   : first_group,
            'is_refund'     : False,
            }

def notify_doctor_of_mod_rejection(request, job, recipient, comments):
    doc_path = reverse('doc_job_page_with_page_and_id', args=[1, job.id])
    notify(request=request,
           notification_type=Notification.JOB_REJECTION,
           description='Please fix a few more things on job ' + str(job.id) + ' - see email',
           recipients=recipient,
           url=doc_path,
           job=job,
           email_args={ 'comments' : comments, 'job' : job }
          )

# you don't need to be skaa or doctor to have the album_approver permission, maybe I should revisit this
# TODO above comment
@require_login_as(['album_approver'])
@render_to("moderator_reject_work.html")
def mod_reject_work(request, job_id):
    profile = request.user

    # you also could say profile.isa('album_approver') but that doesn't make sense to me when I read it
    moderator =  profile.has_perm('common.album_approver')

    if not moderator:
        return redirect( reverse('permission_denied') )

    if request.method == 'POST':
        job = get_object_or_None(Job, id=job_id)
        if job:

            job.status = Job.DOCTOR_ACCEPTED
            job.save()

            comments = request.POST['comment']

            # send a message to doctor
            #send_job_status_change(request, job, job.skaa, "  Feedback: " + comments)
            notify_doctor_of_mod_rejection(request, job, job.doctor, comments)

            return redirect(reverse('album_approval_page'))
        else:
            return redirect( reverse('permission_denied') )


    return  {
            'job_id'        : job_id,
            }



def reject_belongs(request, job_id):
    profile = get_profile_or_None(request)
    job = get_object_or_None(Job, id=job_id)

    if not job or not profile:
        return False

    if job.skaa != profile:
        return False

    return True

@require_login_as(['skaa'])
def refund_user_endpoint(request):
    profile = get_profile_or_None(request)
    data = simplejson.loads(request.body)
    job = get_object_or_None(Job, id=data['job_id'])

    if job and profile and job.skaa == profile:
        # Don't actually have to refund them, because they
        job.bp_hold.delete()
        job.bp_hold.save()

        job.status = Job.REFUND
        job.save()

        send_job_status_change(request, job, profile)

    result = { 'relocate' : reverse('job_page') }
    response_data = simplejson.dumps(result)
    return HttpResponse(response_data, mimetype='application/json')

def notify_doc_of_switch(request, job):
    """
    Let the doctor associated with a job know that the user
    has chosen to 'switch' doctors, so they are out. Bummer.
    """

    job_url = reverse('doc_job_page_with_page_and_id', args=[1, job.id])

    notify(
            request=request,
            notification_type=Notification.JOB_SWITCHED,
            description="%s has chosen to switch doctors on job %d" % (job.skaa.nickname, job.id),
            recipients=job.doctor,
            url=job_url,
            job=job,
            email_args={ 'job' : job },
          )

@require_login_as(['skaa'])
def switch_doctor_endpoint(request):
    profile = get_profile_or_None(request)
    data = simplejson.loads(request.body)
    job = get_object_or_None(Job, id=int(data['job_id']))

    if job and job.skaa == profile:
        notify_doc_of_switch(request, job)
        remove_previous_doctor(job)

    result = { 'relocate' : reverse('job_page') }
    response_data = simplejson.dumps(result)
    return HttpResponse(response_data, mimetype='application/json')

def remove_previous_doctor(job):
    if not job:
        return

    job.status = Job.IN_MARKET
    if job.doctor:
        job.ignore_last_doctor = job.doctor
    job.doctor = None
    job.approved = False
    job.payout_price_cents = 0
    job.save()

    groups = Group.get_job_groups(job)

    for group in groups:
        group.delete_doctor_pics()


