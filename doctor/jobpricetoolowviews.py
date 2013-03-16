# Create your views here.
from django.contrib.auth.decorators import login_required
from django.utils import simplejson
from django.http import HttpResponse
from django.shortcuts import redirect
from django.core.urlresolvers import reverse

from annoying.decorators import render_to

from common.models import *
from common.functions import get_profile_or_None
from common.balancedfunctions import get_merchant_account, get_withdraw_jobs, is_merchant, credit_doctor

import settings
import ipdb

@login_required
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
                'job_price'      : float(job.bp_hold.cents)/100,
                }

    elif request.method == "POST":
        job_price_too_low_action(request, job)
        return redirect( reverse('new_job_page'))

def job_price_too_low_action(request, job):
    doc = get_profile_or_None(request)

    # if the job exists and doesn't have a doctor yet
    if job:
        if not job.doctor:
            too_low_contributor = PriceToLowContributor.objects.filter(job=job.id).filter(doctor=doc.id)
            if len(too_low_contributor) == 0:
                job_qs = Job.objects.select_for_update().filter(pk=job.id)
                for job in job_qs:
                    job.price_too_low_count += 1
                    job.save()
                    price = max(job.bp_hold.cents, int(float(request.POST['price'])*100))
                    contrib=PriceToLowContributor(job=job, doctor=doc, price=price)
                    contrib.save()
