from django.template import RequestContext
from notifications.models import Notification, NotificationToIgnore
from django.core.urlresolvers import reverse
import ipdb
import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from tasks.tasks import sendAsyncEmail
import logging


def notify(notification_type, description, notification, recipients, url):
    # who am I supposed to notify if recipients is None????
    if recipients is None:
        logging.error("attempted to send notification '%s' without recipient" % notification)
        return
    
    # don't feel like sending [profile] be lazy and send profile
    if not isinstance(recipients, list):
        recipients = [recipients]

    # go through each recipient and notify them!
    for recipient in recipients:
        n = Notification()
        n.notification_type = notification_type
        n.description = description
        n.notification = notification
        n.recipient = recipient
        n.url = url
        n.save()

        send_email(n)

def send_email(notification):
    if not i_want_this_email(notification.recipient, notification.notification_type):
        return

    try:
        to_email = notification.recipient.email

        subject = notification.description

        message = notification.notification

        url = reverse('notification_redirecter', args=[notification.id])
        
        args = {
                'message'           : message,
                'site_path'         : url,
                } 
        html_content = render_to_string('notification_email.html', args, RequestContext(request))
                                        
        
        # this strips the html, so people will have the text
        text_content = strip_tags(html_content) 
        # create the email, and attach the HTML version as well.
        msg = EmailMultiAlternatives(subject, text_content, 'donotreply@picdoctors.com', [to_email])
        msg.attach_alternative(html_content, "text/html")
        if settings.IS_PRODUCTION:
            sendAsyncEmail.apply_async(args=[msg])
        else:
            sendAsyncEmail(msg)

    except Exception as ex:
        # later I'd like to ignore this, but for now, let's see errors happen
        # raise ex
        pass




def i_want_this_email(profile, notification_type):
    
    if not profile or not notification_type:
        return False

    ignore_cnt = NotificationToIgnore.objects.filter(profile=profile).filter(notification_type=notification_type).filter(ignore=False).count()

    return ignore_cnt == 0

