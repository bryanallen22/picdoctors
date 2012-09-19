from django.db import models
from django.contrib import admin
from django.db.models.query import QuerySet
from django.core.exceptions import FieldError
from django.contrib.auth.models import User


################################################################################
# Some of this comes from:
#   http://stackoverflow.com/questions/809210/django-manager-chaining
# 
# Basically, we (most) all of our classes to be subclasses of DeleteMixin, so
# that instead of deleting objects, we simply mark them deleted. Good for
# recovering from bugs, etc.
################################################################################

################################################################################
# MixinManager
#
# Don't show deleted objects
################################################################################
class MixinManager(models.Manager):    
    def get_query_set(self):
        try:
            return self.model.MixinQuerySet(self.model).filter(deleted=False)
        except FieldError:
            return self.model.MixinQuerySet(self.model)


################################################################################
# BaseMixin
#
# Abstract class. Add things to admin, use MixinManager
################################################################################
class BaseMixin(models.Model):
    admin = models.Manager()
    objects = MixinManager()

    class MixinQuerySet(QuerySet):

        def globals(self):
            try:
                return self.filter(is_global=True)
            except FieldError:
                return self.all()

    class Meta:
        abstract = True


################################################################################
# DeleteMixin
#
# Most things should be a subclass of this. That way they delete by simply
# marking themselves deleted.
################################################################################
class DeleteMixin(BaseMixin):
    deleted = models.BooleanField(default=False)

    class Meta:
        abstract = True

    def delete(self):
        self.deleted = True
        self.save()


################################################################################
# GlobalMixin
#
# Globals, be a subclass of this. 'Nuff said.
################################################################################
class GlobalMixin(BaseMixin):
    is_global = models.BooleanField(default=True)

    class Meta:
        abstract = True


################################################################################
# UserProfile
#
#  Information about the user goes here. This table goes in conjuction with
#  the User table, which is managed by django
################################################################################
class UserProfile(DeleteMixin):
    # This field is required.
    user = models.OneToOneField(User)

    # Other fields here
    accepted_eula = models.BooleanField()

from urlparse import urlparse
import os
import uuid
from StringIO import StringIO
from PIL import Image

from django.core.files.base import ContentFile
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.utils import simplejson

import logging


ungroupedId = 100000  # Make sure that this matches isotope-app.js
thumb_width    = 200 
thumb_height   = 200 
preview_width  = 800 
preview_height = 800

################################################################################
# Pic
################################################################################

class Pic(DeleteMixin):
    batch                = models.ForeignKey('Batch', blank=True, null=True)

    uuid                 = models.CharField(max_length=32, blank=False,
                                            unique=True, db_index=True)
    created              = models.DateField(auto_now_add=True)
    updated              = models.DateField(auto_now=True)
    title                = models.CharField(max_length=60, blank=True, null=True)
    browser_group_id     = models.IntegerField(blank=False, default=ungroupedId)
    group     = models.ForeignKey('Group', blank=True, null=True, on_delete=models.SET_NULL)
    original             = models.ImageField(upload_to = 'user_originals/')
    preview              = models.ImageField(upload_to = 'user_preview/')
    thumbnail            = models.ImageField(upload_to = 'user_thumbs/')
    general_instructions = models.TextField(blank=True)

    # Getting these later requires fetching the picture.
    # That's oh so very bad. Don't do that.
    original_width       = models.SmallIntegerField(blank=True, null=True)
    original_height      = models.SmallIntegerField(blank=True, null=True)
    preview_width        = models.SmallIntegerField(blank=True, null=True)
    preview_height       = models.SmallIntegerField(blank=True, null=True)
    thumb_width          = models.SmallIntegerField(blank=True, null=True)
    thumb_height         = models.SmallIntegerField(blank=True, null=True)

    def __unicode__(self):
        return self.title

    def set_file(self, myfile):
        my_uuid = uuid.uuid4().hex # 32 unique hex chars

        file_root, file_ext = os.path.splitext(myfile.name)
        file_name = my_uuid + file_ext.lower() # append '.jpg', etc
        myfile.name = file_name

        self.uuid      = my_uuid
        self.title     = file_root # Not the full myfile name, just the root

        # Save original picture, its width and height
        self.original.save(file_name, myfile)
        # TODO -- this fetches the image all over again. Me no likey.
        # Find some other way?
        self.original_width = self.original.width
        self.original_height = self.original.height

        # Save preview picture, its width and height
        preview, self.preview_width, self.preview_height = \
                self.create_thumbnail(myfile, preview_width, preview_height)
        self.preview.save(file_name, preview)
        #self.preview_width  = self.preview.width
        #self.preview_height = self.preview.height

        # Save thumb picture, its width and height
        thumb, self.thumb_width, self.thumb_height = \
                self.create_thumbnail(preview, thumb_width, thumb_height)
        self.thumbnail.save(file_name, thumb)
        #self.thumb_width  = self.thumbnail.width
        #self.thumb_height = self.thumbnail.height

    def get_size(self):
        return self.original.size

    def get_original_url(self):
        return Pic.aws_public_url(self.original.url)

    def get_preview_url(self):
        return Pic.aws_public_url(self.preview.url)

    def get_thumb_url(self):
        return Pic.aws_public_url(self.thumbnail.url)

    # I don't like this hack. I don't know how else to do it.
    # The s3 folder is public, but the django-storages backend
    # embeds my access key into the url. Strip that stuff out
    # here.
    @staticmethod
    def aws_public_url(url):
        parsed = urlparse(url)
        return 'http://' + parsed.netloc + parsed.path

    # See here:
    # http://codespatter.com/2008/09/13/quick-thumbnails-in-django/
    # There's some magic going on with GIF files there. Seems cool,
    # not totally understood yet. Whee for copy paste google code!
    # (ducks his head in shame)
    def create_thumbnail(self, file, width, height):
        logging.info('got to %s' % __name__)
        try:
            size = width, height
            tmp_file = StringIO() # We'll return this as an image
            im = Image.open(StringIO(file.read()))
            format = im.format # since new im won't have format
            if format == "gif" or format == "GIF":
                im = im.convert("RGB")
            im.thumbnail(size, Image.ANTIALIAS)
            if format == "gif" or format == "GIF":
                im = im.convert("P", dither=Image.NONE, palette=Image.ADAPTIVE)
            im.save(tmp_file, format, quality=95)
        except IOError:
            return None
        finally:
            # Take pointer back to the beginning of the file
            file.seek(0)

        # Tuple returned: (image, width, height)
        return (ContentFile(tmp_file.getvalue()),)  + im.size

    def get_markups_json(self):
        # These imports can't be at the top, because they cause a circular depedency
        from skaa.models import Markup
        from skaa.markupviews import markup_to_dict
        if self.uuid is not None:
            markups = Markup.objects.filter(pic__uuid__exact=self.uuid)
            result = [ markup_to_dict(m) for m in markups ]
        else:
            result = []
        return simplejson.dumps(result)





################################################################################
# Batch
################################################################################
class Batch(DeleteMixin):
    # This can be blank if they haven't logged in / created a user yet:
    userprofile = models.OneToOneField(UserProfile, blank=True, null=True)

    created     = models.DateField(auto_now_add=True)
    updated     = models.DateField(auto_now=True)
    description = models.TextField(blank=True)
    num_groups  = models.IntegerField(blank=True, null=True)

################################################################################
# Group
# We actually want to be able to delete and recreate these
################################################################################
class Group(models.Model):
    sequence        = models.IntegerField()
    batch           = models.ForeignKey('Batch')
    doctors_pic     = models.ForeignKey('Pic', related_name='doctors_pic', blank=True, null=True)

# Create your models here.
class Job(DeleteMixin):
    #Job status constants
    STATUS_USER_SUBMITTED = 'user_sub' #submitted to doctors
    STATUS_TOO_LOW   = 'too_low' #not worth doctors time
    STATUS_DOCTOR_ACCEPTED  = 'doctor_acc' #doctor accepted
    STATUS_DOCTOR_REQUESTS_ADDITIONAL_INFORMATION = 'doc_need_info'
    STATUS_DOCTOR_SUBMITTED = 'docter_sub' #submitted to user for approval
    STATUS_USER_ACCEPTED    = 'user_acc'   #user accepts the finished product
    STATUS_USER_REQUESTS_ADDITIONAL_WORK = 'user_add' #scope creep
    STATUS_USER_REJECTS     = 'user_rej'   #user rejects product and wants a refund...

    #Job status Choices for the job_status field below
    JOB_STATUS_CHOICES = (
        (STATUS_USER_SUBMITTED, 'User Submitted'),
        (STATUS_TOO_LOW, 'Price Too Low'),
        (STATUS_DOCTOR_ACCEPTED, 'Doctor Accepted Job'),
        (STATUS_DOCTOR_REQUESTS_ADDITIONAL_INFORMATION, 'Doctor Has Requested Additional Info'),
        (STATUS_DOCTOR_SUBMITTED, 'Doctor Submitted Work'),
        (STATUS_USER_ACCEPTED, 'User Accepted Work'),
        (STATUS_USER_REQUESTS_ADDITIONAL_WORK, 'User Has Requested Additional Work'),
        (STATUS_USER_REJECTS, 'User Has Rejected Work'),
    )

    #Never blank, no batch = no job. related_name since Batch already has a FK
    skaa_batch              = models.ForeignKey(Batch, 
                                                related_name='job_user_batch', 
                                                db_index=True)
    #This can be blank, doctor uploads batch later, related_name (see above)
    doctor_batch            = models.ForeignKey(Batch, 
                                                related_name='job_doctor_batch', 
                                                db_index=True, 
                                                blank=True, 
                                                null=True)
    skaa                   = models.ForeignKey(UserProfile, related_name='job_owner')
    doctor                  = models.ForeignKey(UserProfile, related_name='job_doctor',
                                                blank=True, null=True)
    #from something in the billions to 1 penny
    price                   = models.DecimalField(blank=False, 
                                                  max_digits=13, 
                                                  decimal_places=2)

    price_too_low_count     = models.IntegerField(blank=False, 
                                                  default=0)
    #max_length refers to the shorthand versions above
    job_status              = models.CharField(max_length=15, 
                                               choices=JOB_STATUS_CHOICES, 
                                               default=STATUS_USER_SUBMITTED)
