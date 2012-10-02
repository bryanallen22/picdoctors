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


from django.db.models.signals import post_save

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

    # Everyone is a User/Skaa, even if they don't know or care. Some are also doctors
    is_doctor = models.BooleanField()

    def __unicode__(self):
        out = ""
        if self.is_doctor:
            out = "Doctor: " + self.user.username
        else:
            out = "Skaa: " + self.user.username
        return out
            

class SkaaInfo(DeleteMixin):
    user_profile = models.ForeignKey(UserProfile, 
                                        related_name='associated_skaa')

class DoctorInfo(DeleteMixin):
    user_profile = models.ForeignKey(UserProfile, 
                                          related_name='associated_doctor')


def create_user_profile(sender, instance, created, **kwargs):
        if created:
            UserProfile.objects.create(user=instance)

post_save.connect(create_user_profile, sender=User)

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

def get_pic_path(pic_type, instance, filename):
    path = instance.path_owner + "_" + pic_type
    if instance.watermark:
        path += "_watermark"
    path += "/" + filename
    return path

def pic_originals_path(instance, filename):
    return get_pic_path("originals", instance, filename)

def pic_previews_path(instance, filename):
    return get_pic_path("previews", instance, filename)

def pic_thumbnails_path(instance, filename):
    return get_pic_path("thumbnails", instance, filename)

class Pic(DeleteMixin):
    batch                = models.ForeignKey('Batch', blank=True, null=True)

    uuid                 = models.CharField(max_length=32, blank=False,
                                            unique=True, db_index=True)
    created              = models.DateTimeField(auto_now_add=True)
    updated              = models.DateTimeField(auto_now=True)
    title                = models.CharField(max_length=60, blank=True, null=True)
    browser_group_id     = models.IntegerField(blank=False, default=ungroupedId)
    group                = models.ForeignKey('Group', blank=True, null=True, on_delete=models.SET_NULL)
    original             = models.ImageField(upload_to = pic_originals_path)
    preview              = models.ImageField(upload_to = pic_previews_path)
    thumbnail            = models.ImageField(upload_to = pic_thumbnails_path)
    #The next two fields are used for generating the path
    path_owner           = models.CharField(max_length = 5, blank=False, default="user")
    watermark            = models.BooleanField(blank=False, default=False)
    
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
    userprofile = models.ForeignKey(UserProfile, blank=True, 
                                    null=True, db_index=True)
    created     = models.DateTimeField(auto_now_add=True)
    updated     = models.DateTimeField(auto_now=True)
    description = models.TextField(blank=True)
    num_groups  = models.IntegerField(blank=True, null=True, default=0)
    # This only becomes true after they've paid
    finished    = models.BooleanField(default=False)

    def __unicode__(self):
        if self.userprofile is not None:
            return "Batch # " + str(self.id) + " -- owned by: " + self.userprofile.user.username
        else:
            return "Batch # " + str(self.id) + " -- owned by the internet"  

################################################################################
# Group
# We actually want to be able to delete and recreate these
################################################################################
class Group(models.Model):
    sequence        = models.IntegerField()
    batch           = models.ForeignKey('Batch')
    is_locked       = models.BooleanField(default=False)
 
    def add_doctor_pic(self, pic):
        doc = DocPicGroup(group=self, pic=pic, watermark_pic=pic)
        doc.save()
        return doc

    def get_doctor_pics(self):
        return DocPicGroup.objects.filter(group=self).order_by('updated')

    def __unicode__(self):
        if self.doctors_pic is not None:
            return "Group # " + str(self.id) + " -- is_locked: " + str(self.is_locked) + " -- has doc pic"
        else:
            return "Group # " + str(self.id) + " -- is_locked: " + str(self.is_locked) + " -- No doc pic"


# Doc Pic Group allows us to keep track of all pictures uploaded 
# by a group for a group of pics from the user
class DocPicGroup(DeleteMixin):
    group           = models.ForeignKey(Group, related_name='doc_pic_group')
    pic             = models.ForeignKey(Pic)
    watermark_pic   = models.ForeignKey(Pic, related_name='watermark_pic')
    created         = models.DateTimeField(auto_now_add=True)
    updated         = models.DateTimeField(auto_now=True)


# Create your models here.
class Job(DeleteMixin):
    #Job status constants
    USER_SUBMITTED = 'user_sub' #submitted to doctors
    TOO_LOW   = 'too_low' #not worth doctors time
    DOCTOR_ACCEPTED  = 'doctor_acc' #doctor accepted
    DOCTOR_REQUESTS_ADDITIONAL_INFORMATION = 'doc_need_info'
    DOCTOR_SUBMITTED = 'docter_sub' #submitted to user for approval
    USER_ACCEPTED    = 'user_acc'   #user accepts the finished product
    USER_REQUESTS_ADDITIONAL_WORK = 'user_add' #scope creep
    USER_REJECTS     = 'user_rej'   #user rejects product and wants a refund...

    #Job status Choices for the job_status field below
    JOB_STATUS_CHOICES = (
        (USER_SUBMITTED, 'User Submitted'),
        (TOO_LOW, 'Price Too Low'),
        (DOCTOR_ACCEPTED, 'Doctor Accepted Job'),
        (DOCTOR_REQUESTS_ADDITIONAL_INFORMATION, 'Doctor Has Requested Additional Info'),
        (DOCTOR_SUBMITTED, 'Doctor Submitted Work'),
        (USER_ACCEPTED, 'User Accepted Work'),
        (USER_REQUESTS_ADDITIONAL_WORK, 'User Has Requested Additional Work'),
        (USER_REJECTS, 'User Has Rejected Work'),
    )
    created                 = models.DateTimeField(auto_now_add=True)
    updated                 = models.DateTimeField(auto_now=True)

    #Never blank, no batch = no job. related_name since Batch already has a FK
    skaa_batch              = models.ForeignKey(Batch, 
                                                related_name='skaa_batch', 
                                                db_index=True)
    #This can be blank, doctor uploads batch later, related_name (see above)
    doctor_batch            = models.ForeignKey(Batch, 
                                                related_name='doctor_batch', 
                                                db_index=True, 
                                                blank=True, 
                                                null=True)
    skaa                    = models.ForeignKey(UserProfile, 
                                                related_name='job_owner')
    doctor                  = models.ForeignKey(UserProfile, 
                                                related_name='job_doctor',
                                                blank=True, null=True)
    #from something in the billions to 1 penny
    price                   = models.DecimalField(blank=False, 
                                                  max_digits=13, 
                                                  decimal_places=2)

    #this price is set when a doctor takes the job.  payout prices 
    #that appear on the job page, vary based on accepted job count
    payout_price            = models.DecimalField(blank=True, null=True,
                                                  max_digits=13, 
                                                  decimal_places=2)
    price_too_low_count     = models.IntegerField(blank=False, 
                                                  default=0)
    #max_length refers to the shorthand versions above
    job_status              = models.CharField(max_length=15, 
                                               choices=JOB_STATUS_CHOICES, 
                                               default=USER_SUBMITTED)
    
    def __unicode__(self):
        out = "Owner: " + self.skaa.user.username
        out += " -- Doctor: "
        if self.doctor is None:
            out += "None"
        else:
            out += self.doctor.user.username

        out += " -- price: " + str(self.price)
        out += " -- status: " + self.job_status
        return out
