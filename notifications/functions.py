from notifications.models import Notification, NotificationToIgnore
from django.core.urlresolvers import reverse
import ipdb
import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from tasks.tasks import sendAsyncEmail


def notify(notification_type, notification, recipient, url):
    n = Notification()
    n.notification_type = notification_type
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

        subject = notification.get_notification_type_display()

        message = notification.notification

        url = reverse('notification_redirecter', args=[notification.id])
        
        args = {
                'type'              : subject,
                'message'           : message,
                'site_url'          : settings.SITE_URL,
                'site_path'         : url,
                } 
        html_content = render_to_string('notification_email.html', args)
                                        
        
        # this strips the html, so people will have the text
        text_content = strip_tags(html_content) 
        # create the email, and attach the HTML version as well.
        msg = EmailMultiAlternatives(subject, text_content, 'donotreply@picdoctors.com', [to_email])
        msg.attach_alternative(html_content, "text/html")
        #TODO if you want to switch to using the workers
        # sendAsyncEmail.apply_async(args=[msg])
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

