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
# BPAccountWrapper
################################################################################
class BPAccountWrapper(DeleteMixin):
    """
    Balanced Payment Account - represents either a user or a doctor
    """
    uri = models.CharField(max_length=128, blank=True)

    def fetch(self):
        """
        Go get the object from Balanced. This is slow.
        """
        return balanced.Account.find(uri)

################################################################################
# BPHoldWrapper
################################################################################
class BPHoldWrapper(DeleteMixin):
    """
    Balanced Payment Hold - reserves money for up to 7 days
    """
    uri   = models.CharField(max_length=128, blank=True)

    # Cached info:
    cents = models.IntegerField(blank=False)

    def fetch(self):
        """
        Go get the object from Balanced. This is slow.
        """
        return balanced.Hold.find(uri)

################################################################################
# BPDebitWrapper
################################################################################
class BPDebitWrapper(DeleteMixin):
    """
    Balanced Payment Debit - actual charge of a credit card
    """
    uri   = models.CharField(max_length=128, blank=True)

    # Cached info:
    cents = models.IntegerField(blank=False)

    def fetch(self):
        """
        Go get the object from Balanced. This is slow.
        """
        return balanced.Debit.find(uri)

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

    bp_account_wrapper = models.ForeignKey(BPAccountWrapper, blank=True, null=True)

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
    auto_approve = models.BooleanField(default=False)

    rating       = models.FloatField(default=0.0)

    @staticmethod
    def get_docinfo_or_None(profile):
        info = get_object_or_None(DoctorInfo, user_profile=profile)
        return info

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
    album                = models.ForeignKey('Album', blank=True, null=True)
    uuid                 = models.CharField(max_length=32, blank=False,
                                            unique=True, db_index=True)
    title                = models.CharField(max_length=60, blank=True)
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
        # TODO Why do we care about the original width/height?
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
            file.seek(0) # rewind to beginning of the file
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
# Album
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
#       - Anyone who needs up to date info on the groupings for this album MUST
#         call set_sequences(). The call will only actually set sequences if
#         kick_groups_modified() has been called more recently than set_sequences()
#
################################################################################
class Album(DeleteMixin):
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

    class Meta:
        permissions = (
                ("view_album", "Can view all albums"),
                ("approve_album", "Can approve all albums"),
        )
    
    def get_job_or_None(self):
        job = get_object_or_None(Job, album=self)
        return job

    def get_picture_count(self):
        return Pic.objects.filter(album=self).count()
    
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
        Sets sequence for each picture in the album.

        This method must be called before you can trust any groupings. To
        prevent this method from being overly wasteful, it won't actually
        set any groupings if th`ere hasn't been a call to kick_groups_modified()
        since this method was last called.
        
        Note that this will quite happily override any existing sequence
        that was already set.
        """

        if self.groups_last_modified < self.sequences_last_set:
            logging.info("Album.set_sequences bailing out early - no groups have been modified")
            return

        pics = Pic.objects.filter( album=self )
        logging.info('setting sequences for album_id %d' % self.id)

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
                g = Group(album=self, sequence=next_sequence) 
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
                    g = Group(album=self, sequence=next_sequence) 
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
    def clear_session_album(request):
        """
        Clear the album_id from the session
        """
        if 'album_id' in request.session:
            del request.session['album_id']

    @staticmethod
    def create_album(request):
        """
        Create a album and return it. If the user is logged in, associate this
        album with that user. If not, store it in the session.
        """
        album = Album()

        # Create a album associated with a user
        if request.user.is_authenticated():
            album.userprofile = request.user.get_profile()
            album.save()

        # Create a album and store it in the session
        else:
            album.save()
            Album.clear_session_album(request)
            # Make sure that this stays below the album.save() method so we have an id:
            request.session['album_id'] = album.id

        return album


    @staticmethod
    def get_unfinished(request):
        """
        Returns the unfinished album for either (the logged in user) or (the not
        logged in user, based on their session). Preference is given to logged
        in users if both match.

        If there is more than one unfinished album associated with this user,
        and both album has pictures in it then we raise an exception.
        """

        ret = None

        # If user is logged in, look for one associated with profile
        user_profile = request.user.get_profile() if request.user.is_authenticated() else None
        if user_profile:
            albums = Album.objects.filter(finished=False, userprofile=user_profile)
            empty_album = False
            if len(albums) >= 2:
                # check to see if one of the albums is empty
                for album in albums:
                    if album.get_picture_count() == 0:
                        empty_album = True
                        album.delete()

            # Only requery if we deleted one+ of the albums
            if empty_album:
                albums = Album.objects.filter(finished=False, userprofile=user_profile)

            if len(albums) >= 2:
                raise MultipleObjectsReturned("%s unfinished albums at once!" 
                                              % len(albums))
            elif len(albums) == 1:
                ret = albums[0]

        # If user is not logged in, check the session
        elif 'album_id' in request.session:
            try:
                ret = Album.objects.get(finished=False, pk=request.session['album_id'])
            except Album.DoesNotExist:
                ret = None

        return ret


    def __unicode__(self):
        if self.userprofile is not None:
            return "Album # " + str(self.id) + " -- owned by: " + self.userprofile.user.username
        else:
            return "Album # " + str(self.id) + " -- owned by the internet"  

################################################################################
# Group
# We actually want to be able to delete and recreate these
################################################################################
class Group(models.Model):
    sequence        = models.IntegerField()
    album           = models.ForeignKey('Album', db_index=True)
    is_locked       = models.BooleanField(default=False)
 
    def add_doctor_pic(self, pic, watermark_pic):
        doc = DocPicGroup(group=self, pic=pic, watermark_pic=watermark_pic)
        doc.save()
        return doc

    def has_doctor_pic(self):
        return (DocPicGroup.objects.filter(group=self).count() > 0)

    def get_doctor_pics(self, job, profile):
        if not job:
            return []
        
        moderator =  profile.user.has_perm('common.view_album')

        if job.is_approved() or job.doctor == profile or moderator:
            return DocPicGroup.objects.filter(group=self).order_by('updated').reverse()
            
        return []


    def get_latest_doctor_pic(self, job, profile):
        if not job:
            return []

        moderator =  profile.user.has_perm('common.view_album')

        if job.is_approved() or job.doctor == profile or moderator:
            return DocPicGroup.objects.filter(group=self).order_by('updated').reverse()[:1]
            
        return []

    def delete_doctor_pics(self):
        groups = DocPicGroup.objects.filter(group=self)
        for group in groups:
            #Delete calls save
            group.delete()

    @staticmethod
    def get_album_groups(album):
        return Group.objects.filter(album=album)

    @staticmethod
    def get_job_groups(job):
        return Group.get_album_groups(job.album)

    def __unicode__(self):
        return "Group # " + str(self.id) + " -- is_locked: " + str(self.is_locked)

    
# Doc Pic Group allows us to keep track of all pictures uploaded 
# by a doctor for a combination of pics from the user
class DocPicGroup(DeleteMixin):
    group           = models.ForeignKey(Group, related_name='doc_pic_group', db_index=True)
    pic             = models.ForeignKey(Pic)
    watermark_pic   = models.ForeignKey(Pic, related_name='watermark_pic')

    #I can see me setting a value that flips this from watermark pic to pic
    def get_pic(self, profile, job):
        # if not ( any valid reason to stay ) 
        is_doctor = False if not profile else profile.is_doctor

        # TODO I could get the job in here, but it'd hurt my db feelings
        # job = group.album.get_job_or_None()
        moderator =  profile.user.has_perm('common.view_album')

        if not ( job.is_approved() or is_doctor or moderator ):
            return None

        # I still don't have to return the full pic, just the watermark for now :)
        if job.is_accepted():
            return self.pic
        else:
            return self.watermark_pic

class Job(DeleteMixin):
    #Job status constants
    IN_MARKET = 'in_market' # submitted to doctors
    OUT_OF_MARKET = 'out_market' # out of market
    DOCTOR_ACCEPTED  = 'doctor_acc' # doctor accepted
    DOCTOR_SUBMITTED = 'doctor_sub' # submitted to user for approval
    MODERATOR_APPROVAL_NEEDED = 'mod_need'
    USER_ACCEPTED    = 'user_acc'   # user accepts the finished product
    USER_REJECTED     = 'user_rej'   # user rejects product and wants a refund...
    REFUND            = 'refund'     # user requested refund

    #Job status Choices for the job_status field below
    STATUS_CHOICES = (
        (IN_MARKET, 'Available in Market'),
        (OUT_OF_MARKET, 'Job not taken, consider upping price'),
        (DOCTOR_ACCEPTED, 'Doctor Accepted Job'),
        (DOCTOR_SUBMITTED, 'Doctor Submitted Work'),
        (MODERATOR_APPROVAL_NEEDED, 'Work Submitted, Approval Pending'),
        (USER_ACCEPTED, 'User Accepted Work'),
        (USER_REJECTED, 'User Has Rejected Work'),
        (REFUND, 'Job Refunded'),
    )

    #Never blank, no album = no job. related_name since Album already has a FK
    album                   = models.ForeignKey(Album, 
                                           db_index=True)
    skaa                    = models.ForeignKey(UserProfile, 
                                                related_name='job_owner', 
                                                db_index=True)
    doctor                  = models.ForeignKey(UserProfile, 
                                                related_name='job_doctor',
                                                blank=True, null=True)

    #this price is set when a doctor takes the job.  payout prices 
    #that appear on the job page, vary based on accepted job count
    payout_price_cents      = models.IntegerField(blank=True, null=True)
    
    price_too_low_count     = models.IntegerField(blank=False, 
                                                  default=0)

    # the hold for the charge (good for up to 7 days after creation)
    bp_hold_wrapper         = models.ForeignKey(BPHoldWrapper)

    # the actual debit associated with that hold
    bp_debit_wrapper        = models.ForeignKey(BPDebitWrapper, blank=True, null=True)
    
    # max_length refers to the shorthand versions above
    status                  = models.CharField(max_length=15, 
                                               choices=STATUS_CHOICES, 
                                               default=IN_MARKET, 
                                               db_index=True)
    
    # doc pics are approved for viewing by skaa
    approved                = models.BooleanField(default=False)

    # last communication user
    last_communicator       = models.ForeignKey(UserProfile,
                                                related_name='last_communicator',
                                                blank=True, null=True)
    
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

    def is_approved(self):
        approved = self.approved
        if not approved and self.doctor:
            doc_profile = DoctorInfo.get_docinfo_or_None(self.doctor)
            approved = approved or doc_profile.auto_approve
        return approved

    def is_accepted(self):
        return self.status == Job.USER_ACCEPTED

    def __unicode__(self):
        out = "Owner: " + self.skaa.user.username
        out += " -- Doctor: "
        if self.doctor is None:
            out += "None"
        else:
            out += self.doctor.user.username

        out += " -- price cents: " + str(self.bp_hold_wrapper.cents)
        out += " -- status: " + self.status
        return out

# Keep track of who said the job was too low
# That way you don't have the same doctor say it 50 times
class PriceToLowContributor(DeleteMixin):
    job     = models.ForeignKey(Job, db_index=True)
    doctor  = models.ForeignKey(UserProfile, db_index=True)

# Post switching from a doctor we won't allow them to take that job again
class DocBlock(DeleteMixin):
    job            = models.ForeignKey(Job, db_index=True)
    doctor         = models.ForeignKey(UserProfile)

# Individual Doctor Ratings
class DocRating(DeleteMixin):
    doctor         = models.ForeignKey(UserProfile, db_index=True)
    job            = models.ForeignKey(Job)
    overall_rating = models.IntegerField()
    comments       = models.TextField()

def update_doctor_rating(sender, instance, created, **kwargs):
    ratings = DocRating.objects.filter(doctor=instance.doctor)
    total = 0.0
    for rating in ratings:
        total += rating.overall_rating

    if len(ratings) > 0:
        total /= len(ratings)

    doc_info = DoctorInfo.get_docinfo_or_None(instance.doctor)
    if doc_info:
        doc_info.rating = total
        doc_info.save()

post_save.connect(update_doctor_rating, sender=DocRating)

