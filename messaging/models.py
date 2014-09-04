from django.db import models
from common.models import DeleteMixin, Job, Group
import settings
import uuid
import os

# Create your models here.

class BaseMessage(DeleteMixin):
    commentor         = models.ForeignKey(settings.AUTH_USER_MODEL)
    #Actual Message
    message           = models.TextField(blank=True)
    job               = models.ForeignKey(Job, db_index=True)
    attachment        = models.FileField(upload_to='attachment', blank=True)

    def set_file(self, my_file):
        my_uuid = uuid.uuid4().hex # 32 unique hex chars

        file_root, file_ext = os.path.splitext(myfile.name)
        file_name    = my_uuid + file_ext.lower() # append '.jpg', etc

        my_file.name = file_name
        my_file.content_type = 'application/octet-stream'
        self.attachment = my_file


class JobMessage(BaseMessage):
    # Nothing here as of yet

    @staticmethod
    def get_messages(job):
        return JobMessage.objects.filter(job=job).order_by('created')

class GroupMessage(BaseMessage):
    group             = models.ForeignKey(Group,
                                          db_index=True)

    # IO include the job #, and then filter by job, then group later
    @staticmethod
    def get_messages(group):
        return GroupMessage.objects.filter(group=group).order_by('created')
