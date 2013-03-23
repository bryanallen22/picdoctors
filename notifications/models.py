from django.db import models
from common.models import DeleteMixin, UserProfile

################################################################################
# Markup
#
# Stuff that the user says should change about their picture
################################################################################
class Notification(DeleteMixin):
    JOB_STATUS_CHANGE = 'jb_status_chg' # job status change
    JOBS_AVAILABLE = 'jb_ava' # jobs are available (for spamming doctors)
    JOBS_NEED_APPROVAL = 'jb_need_app' # jobs need approval (for spamming moderators)
    JOB_REMINDER = 'jb_remind' # If a job is waiting on you, remind the user/doctor

    NOTIFICATION_TYPES = (
        (JOB_STATUS_CHANGE, 'Job Status has changed'),
        (JOBS_AVAILABLE, 'Jobs are available'),
        (JOBS_NEED_APPROVAL, 'Jobs need approval'),
        (JOB_REMINDER, 'Job is awaiting you'),
    )

    # max_length refers to the shorthand versions above
    notification_type   = models.CharField(max_length=15, 
                                               choices=NOTIFICATION_TYPES, 
                                               db_index=True)
    
    # the notification to send to the recipient
    notification        = models.CharField(max_length=256, blank=True)

    # the recipient of the notification
    recipient           = models.ForeignKey(UserProfile, db_index=True)

    # the url where they need to go (I think we're going to do a redirect,
    # like all urls are notification/12313, then we redirect to this url
    # if you aren't the recipient of that notification we redirect to zombo.com
    url                 = models.CharField(max_length=256, blank=True)

    # whether or not they've viewed this notification
    viewed              = models.BooleanField(default=False)
    

    @static
    def GetRecentNotifications(recipient, cnt):
        return Notification.objects.filter(recipient=recipient).order_by('created').reverse()[:cnt]


