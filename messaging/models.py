from django.db import models
from common.models import DeleteMixin, UserProfile, Job, Group


# Create your models here.

class BaseMessage(DeleteMixin):
    commentor         = models.ForeignKey(UserProfile)
    #Actual Message
    message           = models.TextField(blank=True)
    #Convenient info for making new messages pop out
    skaa_viewed       = models.BooleanField(default=False)
    doctor_viewed     = models.BooleanField(default=False)

class JobMessage(BaseMessage):
    job               = models.ForeignKey(Job,
                                          db_index=True)

    @staticmethod
    def get_messages(job):
        return JobMessage.objects.filter(job=job).order_by('created')
        
class GroupMessage(BaseMessage):
    job               = models.ForeignKey(Job,
                                          db_index=True) 
                                          
    group             = models.ForeignKey(Group, 
                                          db_index=True)

    # IO include the job #, and then filter by job, then group later
    @staticmethod
    def get_messages(group):
        return GroupMessage.objects.filter(group=group).order_by('created')
