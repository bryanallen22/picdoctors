from datetime import datetime, timedelta
import pytz
from PIL import Image
from StringIO import StringIO
from urlparse import urlparse
import logging; log = logging.getLogger('pd')
import os
import ipdb
import uuid

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.contrib import admin
from django.core.exceptions import MultipleObjectsReturned
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db import models
from django.db.models.signals import post_save
from django.utils import simplejson

from common.basemodels import *
from common.balancedmodels import *
from common.stripemodels import *

from annoying.functions import get_object_or_None

from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

class ProfileUserManager(BaseUserManager):
    def create_user(self, email, password=None, accepted_eula=False):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        email = ProfileUserManager.normalize_email(email)

        user = self.model(
            email=email,
            accepted_eula=accepted_eula,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

class Profile(DeleteMixin, AbstractBaseUser, PermissionsMixin):

    class Meta:
        permissions = (
                ("admin", "Can do everything"),
                ("skaa", "Can do user stuff"),
                ("doctor", "Can do doctor stuff"),
        )

    # manager for creating the user
    objects = ProfileUserManager()


    email                       = models.EmailField( verbose_name='email address', max_length=255, unique=True, db_index=True)
    nickname                    = models.CharField(max_length=32, blank=True, unique=True, db_index=True)

    is_active                   = models.BooleanField(default=True)

    #Required fields for the custom Profile
    USERNAME_FIELD              = 'email'
    REQUIRED_FIELDS             = []

    # Other fields here
    accepted_eula               = models.BooleanField()


    # Doctor Specific - more efficient than joining, allows for skaa/doctor/blah to have important profile fields here

    # associated balanced payment account
    bp_account                  = models.ForeignKey(BPAccount, blank=True, null=True)

    # has this doctor proven they are worthy of being auto approved (no need to be moderated?)
    auto_approve                = models.BooleanField(default=False)

    # Is this doctor any good? (Average rating based on stars, so between 1 and 5)
    rating                      = models.FloatField(default=0.0)

    # how many pics have been approved in the last X days (currently 30)
    approval_pic_count          = models.IntegerField(default=0)
    approval_pic_last_update    = models.DateTimeField(blank=True, null=True)

    # Doctors can have a profile pic
    pic                         = models.ForeignKey('Pic', blank=True, null=True)

    # Description that the doctor puts on their profile
    doc_profile_desc            = models.TextField()

    stripe_customer_id          = models.CharField(max_length=255, blank=True)

    # For the doctor
    stripe_connect              = models.ForeignKey(StripeConnect, blank=True, null=True, default=None)

    # Fixed doctor payout
    # I promised a few people (Jared/others) that they could have a fixed payout amount
    fixed_payout_pct            = models.FloatField(default=0.0)

    def get_full_name(self):
        # The user is identified by their email address
        return self.email

    def get_short_name(self):
        # The user is identified by their email address
        return self.email

    def isa(self, permission):
        return self.has_perm('common.' + permission)

    def has_common_perm(self, permission):
        return self.isa(permission)

    def add_permission(self, permission):
        # So I'm not filtering by the module, since these are our explicitly created permissions
        # Someday when it matters maybe we'll implement this
        #content_type = ContentType.objects.get_for_model(Profile)
        p = Permission.objects.get(codename=permission)
        self.user_permissions.add(p)
        return p

    def remove_permission(self, permission):
        p = Permission.objects.get(codename=permission)
        self.user_permissions.remove(p)

    def __unicode__(self):
        perms = ""
        for p in self.get_all_permissions():
            perms = perms + p + ","

        if len(perms) > 0:
            perms = perms[:-1]

        return "id: " + str(self.id) + " Email: " + self.email + " - Permissions [" + perms + "]"

    def update_approval_count(self):
        self.approval_count = Job.objects.filter(doctor=profile).filter(status=Job.USER_ACCEPTED).count()
        self.save()

    def get_approval_count(self, invalidate=False):
        """
        Return the number of approved pictures in the last <x> days (currently 30)
        """
        from common.functions import get_datetime
        now = get_datetime()
        yesterday = now - timedelta(days=1)
        thirty_ago = now - timedelta(days=30)
        last_update = self.approval_pic_last_update

        if last_update == None or last_update < yesterday or invalidate:

            jobs = Job.objects.filter(doctor=self) \
                    .filter(status=Job.USER_ACCEPTED) \
                    .filter(accepted_date__gte=thirty_ago)

            cnt = 0

            for j in jobs:
                cnt = cnt + j.album.num_groups

            self.approval_pic_last_update = now
            self.approval_pic_count = cnt
            self.save()

        return self.approval_pic_count


################################################################################
# Pic
################################################################################
ungroupedId = 100000  # Make sure that this matches isotope-app.js
default_thumb_width    = 200
default_thumb_height   = 200
default_preview_width  = 800
default_preview_height = 800

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
    path_owner           = models.CharField(max_length=16, blank=False, default="user")
    watermark            = models.BooleanField(blank=False, default=False)

    description          = models.TextField(blank=True)

    # Getting these later requires fetching the picture.
    # That's oh so very bad. Don't do that.
    original_width       = models.SmallIntegerField(blank=True, null=True)
    original_height      = models.SmallIntegerField(blank=True, null=True)
    preview_width        = models.SmallIntegerField(blank=True, null=True)
    preview_height       = models.SmallIntegerField(blank=True, null=True)
    thumb_width          = models.SmallIntegerField(blank=True, null=True)
    thumb_height         = models.SmallIntegerField(blank=True, null=True)

    def __unicode__(self):
        return "id: " + str(self.id) + " " + self.title

    def set_file(self, myfile,
            thumb_width=default_thumb_width, thumb_height=default_thumb_height,
            preview_width=default_preview_width, preview_height=default_preview_height):

        my_uuid = uuid.uuid4().hex # 32 unique hex chars
        log.info('set_file %s' % my_uuid)

        file_root, file_ext = os.path.splitext(myfile.name)
        file_name    = my_uuid + file_ext.lower() # append '.jpg', etc
        preview_name = my_uuid + '.jpg' # always jpg
        thumb_name   = my_uuid + '.jpg' # always jpg
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
        self.preview.save(preview_name, preview)
        #self.preview_width  = self.preview.width  #### SOOOOO SLOOOOW. Has to fetch image all over again.
        #self.preview_height = self.preview.height #### SOOOOO SLOOOOW. Has to fetch image all over again.

        # Save thumb picture, its width and height
        thumb, self.thumb_width, self.thumb_height = \
                self.create_thumbnail(preview, thumb_width, thumb_height)
        self.thumbnail.save(thumb_name, thumb)
        #self.thumb_width  = self.thumbnail.width  #### SOOOOO SLOOOOW. Has to fetch image all over again.
        #self.thumb_height = self.thumbnail.height #### SOOOOO SLOOOOW. Has to fetch image all over again.

    def get_view_model(self, include_markups):
        markupIds = None
        groupId = None

        if include_markups:
            from skaa.models import Markup
            markups = Markup.objects.filter(pic__id=self.id)
            markupIds = [m.id for m in markups]

        if self.group is not None:
            groupId = self.group.id

        model = {
            'id': self.id,
            'group': groupId,
            'description': self.description,
            'preview_url': self.get_preview_url(),
            'original_url': self.get_original_url(),
            'width': self.preview_width,
            'height': self.preview_height,
            'markups': markupIds,
            'created': self.created.isoformat(' ')
            }

        return model

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
        return 'https://' + parsed.netloc + parsed.path

    # See here:
    # http://codespatter.com/2008/09/13/quick-thumbnails-in-django/
    # There's some magic going on with GIF files there. Seems cool,
    # not totally understood yet. Whee for copy paste google code!
    # (ducks his head in shame)
    def create_thumbnail(self, file, width, height):
        try:
            size = width, height
            tmp_file = StringIO() # We'll return this as an image
            file.seek(0) # rewind to beginning of the file
            im = Image.open(StringIO(file.read()))
            format = 'JPEG' # all thumbnails have to be JPEGs. Original can remain TIF or whatever.
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
        markups = self.get_markups()
        return simplejson.dumps(markups)

    def get_markups(self):
        # These imports can't be at the top, because they cause a circular depedency
        from skaa.models import Markup
        from skaa.markupviews import markup_to_dict
        if self.uuid is not None:
            markups = Markup.objects.filter(pic__id=self.id)
            result = [ markup_to_dict(m) for m in markups ]
        else:
            result = []
        return result


    @staticmethod
    def get_group_pics(group):
        return Pic.objects.filter(group=group).order_by('created')


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
    userprofile          = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True,
                                             null=True, db_index=True)
    description          = models.TextField(blank=True)
    # what is num groups, the number of pictures?
    num_groups           = models.IntegerField(blank=True, null=True, default=0)

    # This only becomes true after they've paid (set a hold)
    finished             = models.BooleanField(default=False)

    # If sequences_last_set gets behind groups_last_modified, we know that we
    # need to reorder our sequences
    groups_last_modified = models.DateTimeField(auto_now_add=True)
    sequences_last_set   = models.DateTimeField(auto_now_add=True)

    # Can we show this album publicly?
    allow_publicly       = models.BooleanField(default=False)

    class Meta:
        permissions = (
                ("album_approver", "Can approve all albums"),
        )

    def get_job_or_None(self):
        job = get_object_or_None(Job, album=self)
        return job

    def get_picture_count(self):
        return Pic.objects.filter(album=self).count()

    def kick_groups_modified(self):
        from common.functions import get_datetime
        """
        Any time groupings are modified, call this. (Upload a new pic, delete a pic,
        create or delete a grouping). This allows us to do lazy group setting with
        set_sequences()
        """
        self.groups_last_modified = get_datetime()
        self.save()

    def set_sequences(self, force=False):
        from common.functions import get_datetime
        """
        Sets sequence for each picture in the album.

        This method must be called before you can trust any groupings. To
        prevent this method from being overly wasteful, it won't actually
        set any groupings if th`ere hasn't been a call to kick_groups_modified()
        since this method was last called.

        Note that this will quite happily override any existing sequence
        that was already set.
        """

        if not force and self.groups_last_modified < self.sequences_last_set:
            #log.info("Album.set_sequences bailing out early - no groups have been modified")
            return

        pics = Pic.objects.filter( album=self )
        log.info('setting sequences for album_id %d' % self.id)

        # This doesn't feel like the most efficient way to get a sorted,
        # unique list, but it works
        browser_ids = sorted(list(set([pic.browser_group_id for pic in pics])))
        log.info(browser_ids)
        next_sequence = 1
        for id in browser_ids:
            log.info('browser id: %d' % id)

            # Find all pics that match this id
            matches = pics.filter( browser_group_id__exact=id )
            if id != ungroupedId:
                # All matching pics get next_sequence
                log.info('id != ungroupedId - creating new group sequence %d' % next_sequence)
                g = Group(album=self, sequence=next_sequence)
                g.save()
                for pic in matches:
                    log.info('setting group to pic')
                    #pic.group_id = next_sequence
                    pic.group = g
                    pic.save()
                next_sequence += 1
            else:
                # All ungrouped pics get their own sequence
                log.info('id == ungroupedId - creating new group')
                for pic in matches:
                    log.info('creating new group sequence %d' % next_sequence)
                    g = Group(album=self, sequence=next_sequence)
                    g.save()
                    #pic.group_id = next_sequence
                    pic.group = g
                    pic.save()
                    next_sequence += 1

        next_sequence -= 1
        log.info('Saving number of groups %d' % next_sequence)

        self.num_groups = next_sequence
        self.sequences_last_set = get_datetime()
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
            album.userprofile = request.user
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
        user_profile = request.user if request.user.is_authenticated() else None
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
            return "id " + str(self.id) + " -- owned by: " + self.userprofile.email
        else:
            return "id " + str(self.id) + " -- owned by the internet"

################################################################################
# Group
# We delete and recreate these
################################################################################
class Group(DeleteMixin):
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

        approved = job.is_approved()
        jobDoctor = job.doctor == profile
        approver = profile.has_common_perm('album_approver')

        if approved or jobDoctor or approver:
            return DocPicGroup.objects.filter(group=self).order_by('updated').reverse()

        return []


    def get_latest_doctor_pic(self, job, profile):
        if not job:
            return []

        if job.is_approved() or job.doctor == profile or ( profile and profile.has_common_perm('album_approver') ):
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
        return "id " + str(self.id) + " -- is_locked: " + str(self.is_locked)


# Doc Pic Group allows us to keep track of all pictures uploaded
# by a doctor for a combination of pics from the user
class DocPicGroup(DeleteMixin):
    group           = models.ForeignKey(Group, related_name='doc_pic_group', db_index=True)
    pic             = models.ForeignKey(Pic)
    watermark_pic   = models.ForeignKey(Pic, related_name='watermark_pic')

    def get_view_model(self, profile, job):
        # if not ( any valid reason to stay )
        ret = {'id':self.id, 'group': self.group.id, 'pic': None, 'watermark_pic': None}
        is_doctor = False if not profile else profile.isa('doctor')
        approver = profile.has_common_perm('album_approver')
        if not ( job.is_approved() or is_doctor or approver ):
            return None

        user_accepted = job.skaa == profile and job.is_accepted()
        job_doctor = job.doctor == profile
        job_owner = job.skaa == profile

        if job_doctor or approver or user_accepted:
            ret["pic"] = self.pic.id

        if job_owner or job_doctor:
            ret["watermark_pic"] = self.watermark_pic.id

        return ret

    #I can see me setting a value that flips this from watermark pic to pic
    def get_pic(self, profile, job):
        # if not ( any valid reason to stay )
        is_doctor = False if not profile else profile.isa('doctor')

        if not ( job.is_approved() or is_doctor or ( profile and profile.has_common_perm('album_approver') ) ):
            return None

        # I still don't have to return the full pic, just the watermark for now :)
        if job.is_accepted():
            return self.pic
        else:
            return self.watermark_pic

class Job(DeleteMixin):
    # Job status constants
    IN_MARKET                 = 'in_market'  # submitted to doctors
    OUT_OF_MARKET             = 'out_market' # out of market
    DOCTOR_ACCEPTED           = 'doctor_acc' # doctor accepted
    DOCTOR_SUBMITTED          = 'doctor_sub' # submitted to user for approval
    MODERATOR_APPROVAL_NEEDED = 'mod_need'
    USER_ACCEPTED             = 'user_acc'   # user accepts the finished product
    REFUND                    = 'refund'     # user requested refund

    #Job status Choices for the job_status field below
    STATUS_CHOICES = (
        (IN_MARKET,                 'Available in Market' ),
        (OUT_OF_MARKET,             'Job not taken, consider upping price' ),
        (DOCTOR_ACCEPTED,           'Doctor Accepted Job' ),
        (DOCTOR_SUBMITTED,          'Doctor Submitted Work' ),
        (MODERATOR_APPROVAL_NEEDED, 'Work Submitted, Pending Moderator Approval' ),
        (USER_ACCEPTED,             'User Accepted Work' ),
        (REFUND,                    'Job Refunded' ),
    )

    #Never blank, no album = no job. related_name since Album already has a FK
    album                   = models.ForeignKey(Album,
                                                db_index=True)
    skaa                    = models.ForeignKey(settings.AUTH_USER_MODEL,
                                                related_name='job_owner',
                                                db_index=True)
    doctor                  = models.ForeignKey(settings.AUTH_USER_MODEL,
                                                related_name='job_doctor',
                                                blank=True, null=True)

    ignore_last_doctor      = models.ForeignKey(settings.AUTH_USER_MODEL,
                                                related_name='job_block_doctor',
                                                blank=True, null=True)

    #this price is set when a doctor takes the job.  payout prices
    #that appear on the job page, vary based on accepted job count
    payout_price_cents      = models.IntegerField(blank=True, null=True)

    price_too_low_count     = models.IntegerField(blank=False,
                                                  default=0)

    # the hold for the charge (good for up to 7 days after creation)
    bp_hold                 = models.ForeignKey(BPHold, blank=True, null=True)

    # the actual debit associated with that hold
    bp_debit                = models.ForeignKey(BPDebit, blank=True, null=True)

    # You might think that there should be a bp_credit in here. You are wrong.
    # We don't actually issue a credit at the end of every job (to save on ACH fees),
    # so you'll have to look through the various BPDebits for ones with
    # associated_credit == None

    # max_length refers to the shorthand versions above
    status                  = models.CharField(max_length=15,
                                               choices=STATUS_CHOICES,
                                               default=IN_MARKET,
                                               db_index=True)

    # doc pics are approved for viewing by skaa
    approved                = models.BooleanField(default=False)

    # last communication user
    last_communicator       = models.ForeignKey(settings.AUTH_USER_MODEL,
                                                related_name='last_communicator',
                                                blank=True, null=True)

    accepted_date           = models.DateTimeField(blank=True, null=True)

    stripe_job              = models.ForeignKey(StripeJob, blank=True, null=True)

    def cents(self):
        """
        People who got in with balanced jobs still need to be able to view their old jobs
        """
        if self.bp_hold:
            return self.bp_hold.cents
        else:
            return self.stripe_job.cents

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
            approved = self.doctor.auto_approve
        return approved

    def is_accepted(self):
        return self.status == Job.USER_ACCEPTED

    def __unicode__(self):
        out = "id:" + str(self.id)
        out += " Owner: " + self.skaa.email
        out += " Doctor: "
        if self.doctor is None:
            out += "None"
        else:
            out += self.doctor.email

        out += " Price (cents): " + str(self.cents())
        out += " Status: " + self.status
        return out

# Keep track of who said the job was too low
# That way you don't have the same doctor say it 50 times
class PriceTooLowContributor(DeleteMixin):
    job     = models.ForeignKey(Job, db_index=True)
    doctor  = models.ForeignKey(settings.AUTH_USER_MODEL, db_index=True)
    price   = models.IntegerField(default=0)

# Post switching from a doctor we won't allow them to take that job again
class DocBlock(DeleteMixin):
    job            = models.ForeignKey(Job, db_index=True)
    doctor         = models.ForeignKey(settings.AUTH_USER_MODEL)

# Individual Doctor Ratings
class DocRating(DeleteMixin):
    doctor         = models.ForeignKey(settings.AUTH_USER_MODEL, db_index=True)
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

    doc = instance.doctor
    if doc:
        doc.rating = total
        doc.save()

post_save.connect(update_doctor_rating, sender=DocRating)

