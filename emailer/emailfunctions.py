from django.core.mail import EmailMultiAlternatives
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from tasks.tasks import sendAsyncEmail
import logging
import settings

def send_email(request,
               email_address,
               subject,
               template_name,
               # Optional args:
               template_args = { },
               text_content  = None, # defaults to stripped html content
               from_address  = 'contact@picdoctors.com',
               ):
    """
    Generic email function. All sent emails should go through here.
    """
    html_content  = render_to_string(template_name, template_args, RequestContext(request))
    if not text_content:
        text_content = strip_tags(html_content) 
    msg = EmailMultiAlternatives( subject, text_content, from_address,
                                  [email_address] )
    msg.attach_alternative(html_content, "text/html")

    logging.info("Sending <%s> email to <%s>" % (subject, email_address))
    if settings.IS_PRODUCTION:
        sendAsyncEmail.apply_async(args=[msg])
    else:
        sendAsyncEmail(msg)

