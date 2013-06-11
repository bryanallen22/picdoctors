from django.db import models
from common.models import DeleteMixin, Profile, Job
import settings

from django.db import models
from common.basemodels import *

################################################################################
# Markup
#
# Stuff that the user says should change about their picture
################################################################################
class Notification(DeleteMixin):
    JOB_STATUS_CHANGE  = 'jb_status_chg' # job status change
    JOBS_AVAILABLE     = 'jb_ava'        # jobs are available (for spamming doctors)
    JOBS_NEED_APPROVAL = 'jb_need_app'   # jobs need approval (for spamming moderators)
    JOB_REMINDER       = 'jb_remind'     # If a job is waiting on you, remind the user/doctor
    JOB_MESSAGE        = 'jb_msg'        # A message from a doc/user to user/doc about a job

    NOTIFICATION_TYPES = (
        (JOB_STATUS_CHANGE,  'Job status has changed'),
        (JOBS_AVAILABLE,     'Jobs are available'),
        (JOBS_NEED_APPROVAL, 'Jobs need approval'),
        (JOB_REMINDER,       'Job waiting on you'),
        (JOB_MESSAGE,        'You have received a message about your job'),
    )

    # max_length refers to the shorthand versions above
    notification_type   = models.CharField(max_length=15, 
                                               choices=NOTIFICATION_TYPES, 
                                               db_index=True)
    
    # the notification to send to the recipient
    notification        = models.CharField(max_length=256, blank=True)

    # a short description of this notification (useful for email subjects, and notification drop downs)
    description         = models.CharField(max_length=32, blank=True)

    # the recipient of the notification
    recipient           = models.ForeignKey(settings.AUTH_USER_MODEL, db_index=True)

    # the url where they need to go (I think we're going to do a redirect,
    # like all urls are notification/12313, then we redirect to this url
    # if you aren't the recipient of that notification we redirect to zombo.com
    url                 = models.CharField(max_length=256, blank=True)

    # whether or not they've viewed this notification
    viewed              = models.BooleanField(default=False)

    # This relevant job
    job                 = models.ForeignKey(Job)
    

    @staticmethod
    def GetRecentNotifications(recipient, cnt):
        if not recipient:
            return []
        return Notification.objects.filter(recipient=recipient).order_by('created').reverse()[:cnt]


class NotificationToIgnore(DeleteMixin):
    # max_length refers to the shorthand versions above
    notification_type   = models.CharField(max_length=15, 
                                               choices=Notification.NOTIFICATION_TYPES, 
                                               db_index=True)

    profile             = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, 
                                             null=True, db_index=True)

    # by default we send a notification, unless they've said nayyyyyyy
    ignore              = models.BooleanField(default=True)
    
    
