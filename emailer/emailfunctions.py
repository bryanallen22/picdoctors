from django.core.mail import EmailMultiAlternatives
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from tasks.tasks import sendAsyncEmail
import logging
import settings

def send_email(request,
               email_address,
               template_name,
               # Optional args:
               template_args = { },
               from_address  = 'contact@picdoctors.com',
              ):
    """
    Generic email function. All sent emails should go through here.
    """
    from django.template import loader, Context
    from django.template import loader_tags

    # Directly render nodes in the email templates. This allows us to
    # embed the subject, the plaintext and the html in the same template
    nodes = dict((n.name, n) for n in loader.get_template(template_name).nodelist.get_nodes_by_type(loader_tags.BlockNode))
    con = RequestContext(request)
    con.update(template_args)
    r = lambda n: nodes[n].render(con)

    subject      = r('subject').strip() # be sure to remove newlines
    text_content = r('plain')
    html_content  = render_to_string(template_name, template_args, RequestContext(request))

    msg = EmailMultiAlternatives( subject, text_content, from_address,
                                  [email_address] )
    msg.attach_alternative(html_content, "text/html")

    logging.info("Sending <%s> email to <%s>" % (subject, email_address))
    if settings.IS_PRODUCTION:
        sendAsyncEmail.apply_async(args=[msg])
    else:
        sendAsyncEmail(msg)

