from django.conf.urls import patterns, include, url

from doctor.account_settings_views import create_bank_account, delete_bank_account, merchant_info
from doctor.homeviews import doc_home
from doctor.jobsviews import doc_job_page, new_job_page, apply_for_job 
from doctor.jobsviews import mark_job_completed
from doctor.jobpricetoolowviews import job_price_too_low
from doctor.withdrawviews import withdraw
from doctor.doctorprofileviews import doctor_profile, doctor_profile_pic
from skaa.uploadviews import doc_upload_handler

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
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
    url(r'^create_bank_account/$',                      create_bank_account, name='create_bank_account'),
    url(r'^delete_bank_account/$',                      delete_bank_account, name='delete_bank_account'),
    url(r'^merchant_info/$',                            merchant_info,       name='merchant_info'),
    url(r'^withdraw/$',                                 withdraw,            name='withdraw'),
    url(r'^doctor_profile/(?P<nickname>.+)/',           doctor_profile,      name='doctor_profile'),
    url(r'^doctor_profile_pic/',                        doctor_profile_pic,  name='doctor_profile_pic'),
)

