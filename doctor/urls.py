from django.conf.urls import patterns, include, url

from doctor.homeviews import doc_home
from doctor.jobsviews import doc_job_page, new_job_page, apply_for_job 
from doctor.jobsviews import mark_job_completed, quit_job, quit_job_endpoint
from doctor.jobpricetoolowviews import job_price_too_low
from doctor.doctorprofileviews import doctor_profile
from doctor.faqviews import doc_faq

from skaa.uploadviews import doc_upload_handler

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    url(r'^doc_faq/$',                                  doc_faq,             name='doc_faq'),
    url(r'^doc_jobs/$',                                 doc_job_page,        name='doc_job_page'),
    url(r'^doc_jobs/(?P<page>\d+)$',                    doc_job_page,        name='doc_job_page_with_page'),
    url(r'^doc_jobs/(?P<page>\d+)/(?P<job_id>\d+)/$',   doc_job_page,        name='doc_job_page_with_page_and_id'),
    url(r'^new_jobs/$',                                 new_job_page,        name='new_job_page'),
    url(r'^new_jobs/(?P<page>\d+)$',                    new_job_page,        name='new_job_page_with_page'),
    url(r'^apply_for_job/$',                            apply_for_job,       name='apply_for_job'),
    url(r'^job_price_too_low/(?P<job_id>\d+)/$',        job_price_too_low,   name='job_price_too_low'),
    url(r'^doc_upload_handler/$',                       doc_upload_handler,  name='doc_upload_handler'),
    url(r'^mark_job_completed/$',                       mark_job_completed,  name='mark_job_completed'),
    url(r'^doc_home/$',                                 doc_home,            name='doc_home'),
    url(r'^quit_job/(?P<job_id>\d+)/$',                 quit_job,            name='quit_job'),
    url(r'^quit_job_endpoint/$',                        quit_job_endpoint,   name='quit_job_endpoint'),
    url(r'^doctor_profile/(?P<nickname>.+)/',           doctor_profile,      name='doctor_profile'),
    #email_address=daniel%2Bd4%40picdoctors.com&merchant_uri=%2Fv1%2Fmerchants%2FMR16oahM8RfPpm9oC5ZVaQ0X#bank_tab
)

