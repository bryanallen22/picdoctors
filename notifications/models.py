from django.db import models
from common.models import DeleteMixin, UserProfile

################################################################################
# Markup
#
# Stuff that the user says should change about their picture
################################################################################
class Notification(DeleteMixin):
    notification      = models.CharField(max_length=128, blank=True)
    url               = models.CharField(max_length=256, blank=True)
    viewed            = models.BooleanField(default=False)
    recipient         = models.ForeignKey(UserProfile, db_index=True)
    

    @static
    def GetRecentNotifications(recipient, cnt):
        return Notification.objects.filter(recipient=recipient).order_by('created').reverse()[:cnt]
