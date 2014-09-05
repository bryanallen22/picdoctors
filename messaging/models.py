from django.db import models
from common.models import DeleteMixin, Job, Group
import settings
from urlparse import urlparse
import uuid
import os
import ipdb

# Create your models here.

class BaseMessage(DeleteMixin):
    commentor         = models.ForeignKey(settings.AUTH_USER_MODEL)
    #Actual Message
    message           = models.TextField(blank=True)
    job               = models.ForeignKey(Job, db_index=True)
    attachment        = models.FileField(upload_to='attachments', blank=True, default='')

    def set_file(self, my_file):
        if my_file is None:
            return

        my_uuid = uuid.uuid4().hex # 32 unique hex chars

        file_root, file_ext = os.path.splitext(my_file.name)
        # the client side uses this file name for splitting and showing a friendly name
        file_name = file_root + '-' + my_uuid + file_ext # append '.jpg', etc
        my_file.name = file_name

        my_file.content_type = 'application/octet-stream'
        self.attachment.save(file_name, my_file)

    def get_attachment_url(self):
        print (self.attachment.name)
        if self.attachment.name:
            return BaseMessage.aws_public_url(self.attachment.url)
        return ''

    @staticmethod
    def aws_public_url(url):
        parsed = urlparse(url)
        return 'https://' + parsed.netloc + parsed.path

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
