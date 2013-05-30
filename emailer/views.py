# Create your views here.
from annoying.decorators import render_to
from common.decorators import require_login_as
from emailer.emailfunctions import send_email

import logging

def spam_emails(request, email_address):
    logging.debug("Going to spam %s" % request.POST['email'])

    has = lambda val: val in request.POST and request.POST[val]

    if has('reset_password'):
        send_email(request,
                   email_address=email_address,
                   template_name='reset_password_email.html',
                   template_args={ 'new_password' : 'd1qJUriJAVKJKjPz' }
                  )

@require_login_as(['admin'])
@render_to('debug_spam_emails.html')
def debug_spam_emails(request):
    """
    This should probably be in the admin, but I'm not going to figure it
    out just now.
    """
    if request.method == 'GET':
        return { }
    elif request.method == 'POST':
        if 'email' in request.POST and request.POST['email']:
            spam_emails(request, request.POST['email'])

        else:
            logging.debug('reset_password has no email in POST...')
            return { 'success' : False, 'email_error' : True }

        return {
                 'success' : True,
                 'prefilled_email' : request.POST.get('email', '')
               }

