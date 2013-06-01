# Create your views here.
from annoying.decorators import render_to
from common.decorators import require_login_as
from django.core.urlresolvers import reverse
from emailer.emailfunctions import send_email

import logging

def spam_emails(request, email_address):
    logging.debug("Going to spam %s" % request.POST['email'])

    has = lambda val: val in request.POST and request.POST[val]

    if has('reset_password'):
        send_email(request,
                   email_address=email_address,
                   template_name='reset_password_email.html',
                   template_args={ 'new_password' : 'SOMEPASSWORD' }
                  )
    if has('send_feedback'):
        send_email(request,
                   email_address=email_address,
                   template_name='feedback_email.html',
                   template_args={'from'      : 'someone@example.com',
                                  'feedback'  : "Here is some feedback",
                                  'logged_in' : False },
                  )
    if has('job_price_too_low'):
        site_path = reverse('job_page_with_page_and_id', args=[1, 1])
        send_email(request,
                   email_address=email_address,
                   template_name='job_price_too_low_email.html',
                   template_args= { 'avg_price'             : 12.34,
                                    'job_id'                : 1,
                                    'number_of_doctors'     : 5,
                                    'site_path'             : site_path, })
    if has('new_job'):
        send_email(request,
                   email_address=email_address,
                   template_name='newjob_email.html',
                   template_args={'jobs_url' : reverse( 'job_page' ),
                                  'amount'   : 1234, }, # cents
                  )

@render_to('debug_spam_emails.html')
@require_login_as(['admin'])
def debug_spam_emails(request):
    """
    This should probably be in the admin, but I'm not going to figure it
    out just now.
    """

    checked_boxes = {
                        'reset_password'    : 'checked',
                        'send_feedback'     : 'checked',
                        'job_price_too_low' : 'checked',
                        'new_job'           : 'checked',
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

