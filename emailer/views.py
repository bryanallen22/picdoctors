# Create your views here.
from annoying.decorators import render_to
from common.decorators import require_login_as
from django.core.urlresolvers import reverse
from emailer.emailfunctions import send_email
from common.models import Job

import logging

def send_statuschanges(request, email_address):
    # Be gutsy. Assume there's a job I can steal. This could throw an error -- but I'm too lazy to throw a nice error
    # and it doesn't matter on this page anyway
    job = Job.objects.filter(status=Job.USER_ACCEPTED)[0]
    has = lambda val: val in request.POST and request.POST[val]
    
    # set union of all needed template args
    all_template_args = {
        'job' : job,
    }

    # map html element to the email template
    element_to_template = {
        'jobstatus_doc_doctor_accepted'            : 'jobstatus_doctor_accepted_docemail.html',
        'jobstatus_doc_doctor_submitted'           : 'jobstatus_doctor_submitted_docemail.html',
        'jobstatus_doc_moderator_approval_needed'  : 'jobstatus_moderator_approval_needed_docemail.html',
        'jobstatus_doc_user_accepted'              : 'jobstatus_user_accepted_docemail.html',
        'jobstatus_doc_refund'                     : 'jobstatus_refund_docemail.html',
        'jobstatus_skaa_in_market'                 : 'jobstatus_in_market_skaaemail.html',
        'jobstatus_skaa_out_of_market'             : 'jobstatus_out_of_market_skaaemail.html',
        'jobstatus_skaa_doctor_accepted'           : 'jobstatus_doctor_accepted_skaaemail.html',
        'jobstatus_skaa_doctor_submitted'          : 'jobstatus_doctor_submitted_skaaemail.html',
        'jobstatus_skaa_user_accepted'             : 'jobstatus_user_accepted_skaaemail.html',
        'jobstatus_skaa_refund'                    : 'jobstatus_refund_skaaemail.html',
    }

    for el in element_to_template.keys():
        if has(el):
            logging.debug("Sending email: %s" % element_to_template[el])
            send_email(request,
                       email_address=email_address,
                       template_name=element_to_template[el],
                       template_args=all_template_args
                      )

def spam_emails(request, email_address):
    logging.debug("Going to spam %s" % request.POST['email'])

    has = lambda val: val in request.POST and request.POST[val]

    site_path = reverse('job_page_with_page_and_id', args=[1, 1])
    element_to_template = {
       'reset_password' : 
           (                                                          
               'reset_password_email.html',                             
               { 'new_password'      : 'SOMEPASSWORD' }                 
           ),
       'send_feedback' :
           (
               'feedback_email.html',
               { 'from'              : 'someone@example.com',
                 'feedback'          : "Here is some feedback",
                 'logged_in'         : False }
           ),
       'job_price_too_low' :
           (
               'price_too_low_email.html',
               { 'avg_price'         : 12.34,
                 'job_id'            : 1,
                 'number_of_doctors' : 5,
                 'site_path'         : site_path, }
           ),
       'new_job' :
           (
               'newjob_email.html',
               { 'jobs_url' : reverse( 'job_page' ),
                 'amount'   : 1234, } # cents
           )
    }

    for el in element_to_template.keys():
        if has(el):
            send_email(request,
                       email_address=email_address,
                       template_name=element_to_template[el][0],
                       template_args=element_to_template[el][1],
                      )

    send_statuschanges(request, email_address)


@render_to('debug_spam_emails.html')
@require_login_as(['admin'])
def debug_spam_emails(request):
    """
    This should probably be in the admin, but I'm not going to figure it
    out just now.
    """

    checked_boxes = {
                        'reset_password'                           : 'checked',
                        'send_feedback'                            : 'checked',
                        'job_price_too_low'                        : 'checked',
                        'new_job'                                  : 'checked',
                        'jobstatus_doc_doctor_accepted'            : 'checked',
                        'jobstatus_doc_doctor_submitted'           : 'checked',
                        'jobstatus_doc_moderator_approval_needed'  : 'checked',
                        'jobstatus_doc_user_accepted'              : 'checked',
                        'jobstatus_doc_refund'                     : 'checked',
                        'jobstatus_skaa_in_market'                 : 'checked',
                        'jobstatus_skaa_out_of_market'             : 'checked',
                        'jobstatus_skaa_doctor_accepted'           : 'checked',
                        'jobstatus_skaa_doctor_submitted'          : 'checked',
                        'jobstatus_skaa_user_accepted'             : 'checked',
                        'jobstatus_skaa_refund'                    : 'checked',
                    }

    if request.method == 'GET':
        return checked_boxes
    elif request.method == 'POST':
        if 'email' in request.POST and request.POST['email']:
            spam_emails(request, request.POST['email'])

        else:
            return { 'success' : False, 'email_error' : True }

        # Keep boxes unchecked from last submission
        for choice in checked_boxes.keys():
            if not choice in request.POST:
                checked_boxes[choice] = ''

        ret = {
                'success'         : True,
                'prefilled_email' : request.POST.get('email', '')
              }
        ret.update(checked_boxes)
        return ret

