from urlparse import urlparse
import os
import uuid
from StringIO import StringIO
from PIL import Image

from django.db import models
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.contrib.auth.models import User

import logging

#import pdb


################################################################################
# Pic
################################################################################

class Pic(models.Model):
    group      = models.ForeignKey('Group', blank=True, null=True)
    batch      = models.ForeignKey('Batch', blank=True, null=True)

    created    = models.DateField(auto_now_add=True)
    updated    = models.DateField(auto_now=True)
    title      = models.CharField(max_length=60, blank=True, null=True)
    uuid       = models.CharField(max_length=32, blank=False, unique=True)
    image      = models.ImageField(upload_to='pics/')
    thumbnail  = models.ImageField(upload_to='thumbs/')

    def __unicode__(self):
        return self.title

    def set_file(self, file):
        my_uuid = uuid.uuid4().hex # 32 unique hex chars

        file_root, file_ext = os.path.splitext(file.name)
        file_name = my_uuid + file_ext.lower() # append '.jpg', etc
        file.name = file_name

        self.uuid      = my_uuid
        self.title     = file_root # Not the full file name, just the root
        self.image.save(file_name, file)
        thumb = self.create_thumbnail(file, 200, 200)
        self.thumbnail.save(file_name, thumb)

    def get_size(self):
        return self.image.size

    def get_url(self):
        return Pic.aws_public_url(self.image.url)

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
        #pdb.set_trace()
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

        return ContentFile(tmp_file.getvalue())


################################################################################
# Batch
################################################################################
class Batch(models.Model):
    # This can be blank if they haven't logged in / created a user yet:
    user        = models.OneToOneField(User, blank=True, null=True)

    created     = models.DateField(auto_now_add=True)
    updated     = models.DateField(auto_now=True)
    description = models.TextField(blank=True)


################################################################################
# Markup
#
# Stuff that the user 
################################################################################
class Markup(models.Model):
    pic         = models.ForeignKey('Pic')

    created     = models.DateField(auto_now_add=True)
    # Leave     room for various patterns: '#049CDB' such as 'rgb(100, 100, 100)'
    left        = models.IntegerField(blank=False)
    top         = models.IntegerField(blank=False)
    width       = models.IntegerField(blank=False)
    height      = models.IntegerField(blank=False)
    description = models.TextField(blank=True)


################################################################################
# Group
#
# This represents a single output (photoshopped) image. That means that it can
# be multiple pics or even a single pic.
################################################################################
class Group(models.Model):
    created         = models.DateField(auto_now_add=True)

    # Each batch starts grouping at id=1 (in js), and we keep track of that
    # number here.
    client_group_id = models.IntegerField(blank=False)


################################################################################
# UserProfile
#
#  Information about the user goes here. This table goes in conjuction with
#  the User table, which is managed by django
################################################################################
class UserProfile(models.Model):
    # This field is required.
    user = models.OneToOneField(User)

    # Other fields here
    accepted_eula = models.BooleanField()
    favorite_animal = models.CharField(max_length=20, default="Dragons.")
