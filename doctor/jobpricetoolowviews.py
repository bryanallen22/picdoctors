# Create your views here.
from annoying.decorators import render_to
from common.decorators import require_login_as
from common.functions import get_profile_or_None
from common.models import *
from django.core.urlresolvers import reverse
from django.shortcuts import redirect

import settings
import ipdb

@require_login_as(['doctor'])
@render_to('too_low.html')
def job_price_too_low(request, job_id=None):
    job_id = int(job_id)
    job = get_object_or_None(Job, id=job_id)
    profile = get_profile_or_None(request)
    if not job:
        return redirect('/')

    if request.method == "GET":

        return {
                'pic_count'      : job.album.num_groups,
                'job_price'      : float(job.cents())/100,
                }

    elif request.method == "POST":
        job_price_too_low_action(request, job)
        return redirect( reverse('new_job_page'))

def job_price_too_low_action(request, job):
    doc = get_profile_or_None(request)

    # if the job exists and doesn't have a doctor yet
    if job:
        if not job.doctor:
            too_low_contributor = PriceTooLowContributor.objects.filter(job=job.id).filter(doctor=doc.id)
            if len(too_low_contributor) == 0:
                # If we're here, it's because we need to add this doctor
                # to the PriceTooLowContributor set
                job_qs = Job.objects.select_for_update().filter(pk=job.id)
                for job in job_qs:
                    job.price_too_low_count += 1
                    job.save()
                    price = max(job.cents(), int(float(request.POST['price'])*100))
                    contrib=PriceTooLowContributor(job=job, doctor=doc, price=price)
                    contrib.save()

            if job.price_too_low_count % 5 == 0:
                send_user_email(request, job)

def send_user_email(request, job):
    try:
        contribs = PriceTooLowContributor.objects.filter(job=job.id)
        avg_price = 0

        for contrib in contribs:
            avg_price += contrib.price

        avg_price = avg_price / len(contribs)
        avg_price = float(avg_price) / 100
        site_path = reverse('job_page_with_page_and_id', args=[1, job.id])

        send_email(request,
                   email_address=job.skaa.email,
                   template_name='price_too_low_email.html',
                   template_args= { 'avg_price'             : avg_price,
                                    'job_id'                : job.id,
                                    'number_of_doctors'     : len(contribs),
                                    'site_path'             : site_path, })
        return True
    except Exception as ex:
        return False

