from urlparse import urlparse
import os
import uuid
from StringIO import StringIO
from PIL import Image

from django.db import models
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.contrib.auth.models import User

from util.models import DeleteMixin

import logging

ungroupedId = 100000; # Make sure that this matches isotope-app.js

################################################################################
# Pic
################################################################################

class Pic(DeleteMixin):
    batch            = models.ForeignKey('Batch', blank=True, null=True)

    uuid             = models.CharField(max_length=32, blank=False,
                                        unique=True, db_index=True)
    created          = models.DateField(auto_now_add=True)
    updated          = models.DateField(auto_now=True)
    title            = models.CharField(max_length=60, blank=True, null=True)
    browser_group_id = models.IntegerField(blank=False, default=ungroupedId)

    original         = models.ImageField(upload_to='user_originals/')
    preview          = models.ImageField(upload_to='user_preview/')
    thumbnail        = models.ImageField(upload_to='user_thumbs/')

    def __unicode__(self):
        return self.title

    def set_file(self, myfile):
        my_uuid = uuid.uuid4().hex # 32 unique hex chars

        file_root, file_ext = os.path.splitext(myfile.name)
        file_name = my_uuid + file_ext.lower() # append '.jpg', etc
        myfile.name = file_name

        self.uuid      = my_uuid
        self.title     = file_root # Not the full myfile name, just the root

        self.original.save(file_name, myfile)
        thumb = self.create_thumbnail(myfile, 200, 200)
        self.thumbnail.save(file_name, thumb)
        preview = self.create_thumbnail(myfile, 800, 800)
        self.preview.save(file_name, preview)

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

        return ContentFile(tmp_file.getvalue())


################################################################################
# Batch
################################################################################
class Batch(DeleteMixin):
    # This can be blank if they haven't logged in / created a user yet:
    user        = models.OneToOneField(User, blank=True, null=True)

    created     = models.DateField(auto_now_add=True)
    updated     = models.DateField(auto_now=True)
    description = models.TextField(blank=True)

