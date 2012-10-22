from datetime import datetime
from PIL import Image
from StringIO import StringIO
from urlparse import urlparse
import logging
import os
import pdb
import uuid

from django.contrib.auth.models import User
from django.contrib import admin
from django.core.exceptions import FieldError, MultipleObjectsReturned
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db import models
from django.db.models.query import QuerySet
from django.db.models.signals import post_save
from django.utils import simplejson

from annoying.functions import get_object_or_None

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
    admin   = models.Manager()
    objects = MixinManager()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

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

################################################################################
# Pic
################################################################################
ungroupedId = 100000  # Make sure that this matches isotope-app.js
thumb_width    = 200 
thumb_height   = 200 
preview_width  = 800 
preview_height = 800

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
        logging.info('set_file %s' % my_uuid)

        file_root, file_ext = os.path.splitext(myfile.name)
        file_name = my_uuid + file_ext.lower() # append '.jpg', etc
        myfile.name = file_name

        self.uuid      = my_uuid
        self.title     = file_root # Not the full myfile name, just the root

        # So when we deliver the original jpeg to the user they don't want 
        # it delivered in the browser window do they?
        # I doubt it, I bet they'd like to download the file.  
        # Unfortunately since we can't modify the headers when s3 is serving
        # the file, we are forced to set the content type of the file when saving to s3
        # and then they decide to serve it with the same headers, aka something
        # the browser doesn't want to handle.  Don't worry, we're just changing the
        # original which means when you try and navigate to it's url it will download it
        myfile.content_type = 'application/octet-stream'
        # Save original picture, its width and height
        self.original.save(file_name, myfile)
        # TODO -- this fetches the image all over again. Me no likey.
        # Find some other way?
        # Why not load the image using Pil and get the width/height from it?
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

    @staticmethod
    def get_group_pics(group):
        return Pic.objects.filter(group=group)


################################################################################
# Batch
#
# A word on groupings:
#
#     Groupings are set on the upload page, but setting the full groupings is
#     kinda database intensive, so we don't want to run set_sequences every time
#     anything changes. Instead, we only want to do it when necessary. So,
#
#       - Any time a user modifies the groupings in some way, you must call
#         kick_groups_modified(). Examples: new pic uploaded, grouping created,
#         grouping deleted.
#       - Anyone who needs up to date info on the groupings for this batch MUST
#         call set_sequences(). The call will only actually set sequences if
#         kick_groups_modified() has been called more recently than set_sequences()
#
################################################################################
class Batch(DeleteMixin):
    # This can be blank if they haven't logged in / created a user yet:
    userprofile          = models.ForeignKey(UserProfile, blank=True, 
                                             null=True, db_index=True)
    description          = models.TextField(blank=True)
    num_groups           = models.IntegerField(blank=True, null=True, default=0)
    # This only becomes true after they've paid
    finished             = models.BooleanField(default=False)
    # If sequences_last_set gets behind groups_last_modified, we know that we
    # need to reorder our sequences
    groups_last_modified = models.DateTimeField(auto_now_add=True)
    sequences_last_set   = models.DateTimeField(auto_now_add=True)
    
    def get_job_or_None(self):
        job = get_object_or_None(Job, batch=self)
        return job
    
    def kick_groups_modified(self):
        """
        Any time groupings are modified, call this. (Upload a new pic, delete a pic,
        create or delete a grouping). This allows us to do lazy group setting with
        set_sequences()
        """
        self.groups_last_modified = datetime.now()
        self.save()

    def set_sequences(self):
        """
        Sets sequence for each picture in the batch.

        This method must be called before you can trust any groupings. To
        prevent this method from being overly wasteful, it won't actually
        set any groupings if there hasn't been a call to kick_groups_modified()
        since this method was last called.
        
        Note that this will quite happily override any existing sequence
        that was already set.
        """

        if self.groups_last_modified < self.sequences_last_set:
            logging.info("Batch.set_sequences bailing out early - no groups have been modified")
            return

        pics = Pic.objects.filter( batch=self )
        logging.info('setting sequences for batch_id %d' % self.id)

        # This doesn't feel like the most efficient way to get a sorted,
        # unique list, but it works
        browser_ids = sorted(list(set([pic.browser_group_id for pic in pics])))
        logging.info(browser_ids)
        next_sequence = 1
        for id in browser_ids:
            # Find all pics that match this id
            matches = pics.filter( browser_group_id__exact=id )
            if id != ungroupedId:
                # All matching pics get next_sequence
                logging.info('creating new group')
                g = Group(batch=self, sequence=next_sequence) 
                g.save()
                for pic in matches:
                    #pic.group_id = next_sequence
                    pic.group = g
                    pic.save()
                next_sequence += 1
            else:
                # All ungrouped pics get their own sequence
                for pic in matches:
                    logging.info('creating new group')
                    g = Group(batch=self, sequence=next_sequence) 
                    g.save()
                    #pic.group_id = next_sequence
                    pic.group = g
                    pic.save()
                    next_sequence += 1

        next_sequence -= 1
        logging.info('Saving number of groups %d' % next_sequence)

        self.num_groups = next_sequence
        self.sequences_last_set = datetime.now()
        self.save()

    @staticmethod
    def clear_session_batch(request):
        """
        Clear the batch_id from the session
        """
        if 'batch_id' in request.session:
            del request.session['batch_id']

    @staticmethod
    def create_batch(request):
        """
        Create a batch and return it. If the user is logged in, associate this
        batch with that user. If not, store it in the session.
        """
        batch = Batch()

        # Create a batch associated with a user
        if request.user.is_authenticated():
            batch.userprofile = request.user.get_profile()
            batch.save()

        # Create a batch and store it in the session
        else:
            batch.save()
            Batch.clear_session_batch(request)
            # Make sure that this stays below the batch.save() method so we have an id:
            request.session['batch_id'] = batch.id

        return batch


    @staticmethod
    def get_unfinished(request):
        """
        Returns the unfinished batch for either (the logged in user) or (the not
        logged in user, based on their session). Preference is given to logged
        in users if both match.

        If there is more than one unfinished batch associated with this user,
        something is wrong and we raise an exception.
        """

        ret = None

        # If user is logged in, look for one associated with profile
        user_profile = request.user.get_profile() if request.user.is_authenticated() else None
        if user_profile:
            batches = Batch.objects.filter(finished=False, userprofile=user_profile)
            if len(batches) >= 2:
                raise MultipleObjectsReturned("%s unfinished batches at once!" 
                                              % len(batches))
            elif len(batches) == 1:
                ret = batches[0]

        # If user is not logged in, check the session
        elif 'batch_id' in request.session:
            try:
                ret = Batch.objects.get(finished=False, pk=request.session['batch_id'])
            except Batch.DoesNotExist:
                ret = None

        return ret


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
 
    def add_doctor_pic(self, pic, watermark_pic):
        doc = DocPicGroup(group=self, pic=pic, watermark_pic=watermark_pic)
        doc.save()
        return doc

    def has_doctor_pic(self):
        return (DocPicGroup.objects.filter(group=self).count() > 0)

    def get_doctor_pics(self):
        return DocPicGroup.objects.filter(group=self).order_by('updated').reverse()

    def get_latest_doctor_pic(self):
        return DocPicGroup.objects.filter(group=self).order_by('updated').reverse()[:1]


    @staticmethod
    def get_batch_groups(batch):
        return Group.objects.filter(batch=batch)

    @staticmethod
    def get_job_groups(job):
        return Group.get_batch_groups(job.batch)

    def __unicode__(self):
        return "Group # " + str(self.id) + " -- is_locked: " + str(self.is_locked)

    
# Doc Pic Group allows us to keep track of all pictures uploaded 
# by a group for a group of pics from the user
class DocPicGroup(DeleteMixin):
    group           = models.ForeignKey(Group, related_name='doc_pic_group')
    pic             = models.ForeignKey(Pic)
    watermark_pic   = models.ForeignKey(Pic, related_name='watermark_pic')

    #I can see me setting a value that flips this from watermark pic to pic
    def get_pic(self):
        #if accepted self.pic blah blah blah
        return self.watermark_pic


# Create your models here.
class Job(DeleteMixin):
    #Job status constants
    USER_SUBMITTED = 'user_sub' #submitted to doctors
    TOO_LOW   = 'too_low' #not worth doctors time
    DOCTOR_ACCEPTED  = 'doctor_acc' #doctor accepted
    DOCTOR_REQUESTS_ADDITIONAL_INFORMATION = 'doc_need_info'
    DOCTOR_SUBMITTED = 'docter_sub' #submitted to user for approval
    USER_ACCEPTED    = 'user_acc'   #user accepts the finished product
    USER_REQUESTS_MODIFICATION = 'user_add' #scope creep
    USER_REJECTED     = 'user_rej'   #user rejects product and wants a refund...

    #Job status Choices for the job_status field below
    STATUS_CHOICES = (
        (USER_SUBMITTED, 'User Submitted'),
        (TOO_LOW, 'Price Too Low'),
        (DOCTOR_ACCEPTED, 'Doctor Accepted Job'),
        (DOCTOR_REQUESTS_ADDITIONAL_INFORMATION, 'Doctor Has Requested Additional Info'),
        (DOCTOR_SUBMITTED, 'Doctor Submitted Work'),
        (USER_ACCEPTED, 'User Accepted Work'),
        (USER_REQUESTS_MODIFICATION, 'User Has Requested Some Modification'),
        (USER_REJECTED, 'User Has Rejected Work'),
    )

    #Never blank, no batch = no job. related_name since Batch already has a FK
    batch              = models.ForeignKey(Batch, 
                                           db_index=True)
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
    status                  = models.CharField(max_length=15, 
                                               choices=STATUS_CHOICES, 
                                               default=USER_SUBMITTED)
    
    def is_part_of(self, profile):
        if not profile:
            return False
        return self.skaa == profile or self.doctor == profile

    def get_first_unfinished_group(self):
        groups = Group.get_job_groups(self)
        for group in groups:
            if not group.has_doctor_pic():
                return group

        return None

    def __unicode__(self):
        out = "Owner: " + self.skaa.user.username
        out += " -- Doctor: "
        if self.doctor is None:
            out += "None"
        else:
            out += self.doctor.user.username

        out += " -- price: " + str(self.price)
        out += " -- status: " + self.status
        return out

