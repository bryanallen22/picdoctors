from notifications.models import Notification, NotificationToIgnore
from django.core.urlresolvers import reverse
import ipdb
import settings
import logging; log = logging.getLogger('pd')

from emailer.emailfunctions import send_email
from common.models import Job

def notify(request, notification_type, description, recipients, url, job, email_args):
    """
    Send an in-site notification as well as an email

    request           -- obvious
    notification_type -- corresponds to the top of Notification class -- e.g. JOB_STATUS_CHANGE
    description       -- a few words of title
    recipients        -- a list of profiles
    url               -- to what url is this notification directing the user?
    job               -- obvious
    email_args        -- arguments handed over to the email (more may be added below this call in send_notification_email)
    """

    # who am I supposed to notify if recipients is None????
    if recipients is None:
        log.error("attempted to send notification '%s' without any recipients! (job %d)" % (description, job.id))
        return

    # don't feel like sending [profile] be lazy and send profile
    if not isinstance(recipients, list):
        recipients = [recipients]

    # go through each recipient and notify them!
    for recipient in recipients:
        n = Notification()
        n.notification_type = notification_type
        n.description = description
        n.recipient = recipient
        n.url = url
        n.job = job
        n.save()

        send_notification_email(request, n, email_args)

def send_jobstatus_email(request, notification, url):
    # So, this is kinda confusing, but we're not going to use
    # notification.description or notification.notification, because those
    # are very short and don't make good emails. (They make excellent
    # drop down site reminders, though.) Instead, different job states
    # get mapped to entirely different emails.

    job = notification.job

    if job.doctor == notification.recipient:
        # In the name of simplicity, all of these are passed to each template, even if they
        # are not all needed for that template
        all_template_args = {
            'job' : job,
        }
        email_templ = {
            Job.IN_MARKET                 : None,
            Job.OUT_OF_MARKET             : None,
            Job.DOCTOR_ACCEPTED           : 'jobstatus_doctor_accepted_docemail.html',
            Job.DOCTOR_SUBMITTED          : 'jobstatus_doctor_submitted_docemail.html',
            Job.MODERATOR_APPROVAL_NEEDED : 'jobstatus_moderator_approval_needed_docemail.html',
            Job.USER_ACCEPTED             : 'jobstatus_user_accepted_docemail.html',
            Job.REFUND                    : 'jobstatus_refund_docemail.html',
        }
    elif job.skaa == notification.recipient:
        all_template_args = {
            'job' : job,
        }
        email_templ = {
            Job.IN_MARKET                 : 'jobstatus_in_market_skaaemail.html',
            Job.OUT_OF_MARKET             : 'jobstatus_out_of_market_skaaemail.html',
            Job.DOCTOR_ACCEPTED           : 'jobstatus_doctor_accepted_skaaemail.html',
            Job.DOCTOR_SUBMITTED          : 'jobstatus_doctor_submitted_skaaemail.html',
            Job.MODERATOR_APPROVAL_NEEDED : None,
            Job.USER_ACCEPTED             : 'jobstatus_user_accepted_skaaemail.html',
            Job.REFUND                    : 'jobstatus_refund_skaaemail.html',
        }

    if email_templ[job.status]:
        send_email(request,
                   email_address=notification.recipient.email,
                   template_name=email_templ[job.status],
                   template_args=all_template_args,
                  )

def send_notification_email(request, notification, email_args):
    if not i_want_this_email(notification.recipient, notification.notification_type):
        return

    url = reverse('notification_redirecter', args=[notification.id])

    if notification.notification_type == Notification.JOB_STATUS_CHANGE:
        send_jobstatus_email(request, notification, url)
    elif notification.notification_type == Notification.JOB_MESSAGE:
        email_args['job'] = notification.job
        send_email(
                      request=request,
                      email_address=notification.recipient.email,
                      template_name='comment_email.html',
                      template_args=email_args
                  )
    elif notification.notification_type == Notification.JOBS_AVAILABLE:
        log.error("email for JOBS_AVAILABLE not yet implemented!")
        assert(False)
    elif notification.notification_type == Notification.JOBS_NEED_APPROVAL:
        log.error("email for JOBS_NEED_APPROVAL not yet implemented!")
        assert(False)
    elif notification.notification_type == Notification.JOB_REMINDER:
        log.error("email for JOB_REMINDER not yet implemented!")
        assert(False)
    elif notification.notification_type == Notification.JOB_REJECTION:
        send_email(
                      request=request,
                      email_address=notification.recipient.email,
                      template_name='job_rejection_email.html',
                      template_args=email_args
                  )
    elif notification.notification_type == Notification.JOB_SWITCHED:
        send_email(
                      request=request,
                      email_address=notification.recipient.email,
                      template_name='doc_switched_email.html',
                      template_args=email_args
                  )

    else:
        log.error("Notification type unknown!")
        assert(False);

def i_want_this_email(profile, notification_type):

    if not profile or not notification_type:
        return False

    ignore_cnt = NotificationToIgnore.objects.filter(profile=profile).filter(notification_type=notification_type).filter(ignore=False).count()

    return ignore_cnt == 0

