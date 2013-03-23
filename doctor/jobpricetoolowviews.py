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
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from tasks.tasks import sendAsyncEmail

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
            too_low_contributor = PriceTooLowContributor.objects.filter(job=job.id).filter(doctor=doc.id)
            if len(too_low_contributor) == 0:
                job_qs = Job.objects.select_for_update().filter(pk=job.id)
                for job in job_qs:
                    job.price_too_low_count += 1
                    job.save()
                    price = max(job.bp_hold.cents, int(float(request.POST['price'])*100))
                    contrib=PriceTooLowContributor(job=job, doctor=doc, price=price)
                    contrib.save()
                    
                if job.price_too_low_count % 5 == 0:
                    send_user_email(job)

def send_user_email(job):
    try:
        to_email = [job.skaa.email]

        subject = "Job price too low"

        contribs = PriceTooLowContributor.objects.filter(job=job.id)
        avg_price = 0

        for contrib in contribs:
            avg_price += contrib.price

        avg_price = avg_price / len(contribs)
        avg_price = float(avg_price) / 100
        site_path = reverse('job_page_with_page_and_id', args=[1, job.id])


        args = {
                'avg_price'             : avg_price,
                'job_id'                : job.id,
                'number_of_doctors'     : len(contribs),
                'site_url'              : settings.SITE_URL,
                'site_path'             : site_path,
                } 
        html_content = render_to_string('job_price_too_low_email.html', args)
                                        
        
        # this strips the html, so people will have the text
        text_content = strip_tags(html_content) 
        # create the email, and attach the HTML version as well.
        msg = EmailMultiAlternatives(subject, text_content, 'donotreply@picdoctors.com', to_email)
        msg.attach_alternative(html_content, "text/html")
        #TODO if you want to switch to using the workers
        # sendAsyncEmail.apply_async(args=[msg])
        sendAsyncEmail(msg)

        return True
    except Exception as ex:
        return False


