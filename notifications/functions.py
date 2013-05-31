from notifications.models import Notification, NotificationToIgnore
from django.core.urlresolvers import reverse
import ipdb
import settings
import logging


def notify(request, notification_type, description, notification, recipients, url):
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

        send_notification_email(request, n)

def send_notification_email(request, notification):
    if not i_want_this_email(notification.recipient, notification.notification_type):
        return

    #subject = notification.description
    message = notification.notification
    url = reverse('notification_redirecter', args=[notification.id])
    
    send_email(request,
               email_address=notification.recipient.email,
               template_name='notification_email.html',
               template_args = { 'message'   : message,
                                 'site_path' : url },
              )

def i_want_this_email(profile, notification_type):
    
    if not profile or not notification_type:
        return False

    ignore_cnt = NotificationToIgnore.objects.filter(profile=profile).filter(notification_type=notification_type).filter(ignore=False).count()

    return ignore_cnt == 0

