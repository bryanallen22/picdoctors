
from django.core.exceptions import MultipleObjectsReturned
from django.core.urlresolvers import reverse
from django.views.decorators.csrf import csrf_exempt
from annoying.functions import get_object_or_None

from common.models import Album

import logging
from datetime import datetime, timedelta
import urllib
import urlparse

import pdb
import pytz

import balanced
import settings

def get_profile_or_None(request):
    """ Get the request user profile if they are logged in """
    if request.user.is_authenticated():
        return request.user.get_profile()
    return None

def get_or_create_balanced_account(request, profile=None):
    # Configure balanced
    if not profile:
        profile = get_profile_or_None(request)
    balanced.configure(settings.BALANCED_API_KEY_SECRET)
    
    # Get their account if they have one
    if profile.bp_account_wrapper:
        account = balanced.Account.find(profile.bp_account_wrapper.uri)
    else:
        # Create a new account and associate it with this profile
        account = balanced.Account().save()
        account.email_address = email_address
        account.save()
        wrapper = BPAccountWrapper(uri=account.uri)
        wrapper.save()
        profile.bp_account_wrapper = wrapper
        profile.save()
   
def get_time_string(prev_date):
    """
    Returns a user friendly string saying how long ago prev_date occurred.
    This is nice because formatting times to the various parts of the world
    is a recipe for disaster.

    The string should fit a sentence like this:
        Uploaded __________.
        
    Examples:
        21 minutes ago
        2 hours ago
        on 10 Oct 2012
    """
    # When comparing against db, we need tz aware utc time
    # I'm not sure what happened, this was working a week ago w/o it.
    # Did we change something?
    now = datetime.utcnow().replace(tzinfo=pytz.UTC)
    yesterday = now - timedelta(days=1)
    hour_ago = now - timedelta(hours=1)

    # Created in the future? (Don't do this.)
    if prev_date > now:
        ret = "in the future, on %s" % (prev_date.isoformat(' '))
        logging.error("get_time_string() for obj in the future! %s" %
                      (prev_date.isoformat(' ')))
    # Created in the last hour?
    elif prev_date > hour_ago:
        delta = now - prev_date
        minutes = int(round(delta.seconds / 60.0)) 
        if minutes == 0:
            ret = "Less than a minute ago"
        elif minutes == 1:
            ret = "%s minute ago" % ( minutes )
        else:
            ret = "%s minutes ago" % ( minutes )

    # Created in the last day?
    elif prev_date > yesterday:
        delta = now - prev_date
        hours = int(round(delta.seconds / 3600.0)) 
        if hours == 1:
            ret = "%s hour ago" % ( hours )
        else:
            ret = "%s hours ago" % ( hours )

    # Created over a day ago
    else:
        ret = "on " + prev_date.strftime("%d %b %Y")

    return ret

def get_unfinished_album(request):
    album = None
    redirect_url = None
    try:
        album = Album.get_unfinished(request)
        if not album:
            redirect_url = reverse('upload')
    except MultipleObjectsReturned:
        # Too many open unfinished albums. Resolve them.

        redirect_url = '%s?next=%s' % (reverse('merge_albums'),
                               urllib.quote( request.get_full_path() ));

    return (album, redirect_url)

from django.contrib.auth.models import Group
from annoying.decorators import render_to
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import EmailMultiAlternatives
from tasks.tasks import sendAsyncEmail


#TODO Remove this
@csrf_exempt
@render_to("gopro.html")
def go_pro(request):
    user = request.user
    moderator = get_object_or_None(Group, name='Album Moderators')
    user.groups.add(moderator)

    send_go_pro_email(request)

    return {}


def send_go_pro_email(request):
    try:
        to_email = 'feedback@picdoctors.com'

        user = request.user

        which_user = user.username
        which_id = user.id


        args = {'which_user':which_user, 'which_id':which_id} 
        html_content = render_to_string('gopro_email.html', args)
                                        
        
        # this strips the html, so people will have the text
        text_content = strip_tags(html_content) 
        # create the email, and attach the HTML version as well.
        msg = EmailMultiAlternatives('user went pro', text_content, 'donotreply@picdoctors.com', [to_email])
        msg.attach_alternative(html_content, "text/html")
        #TODO if you want to switch to using the workers
        # sendAsyncEmail.apply_async(args=[msg])
        sendAsyncEmail(msg)

    except Exception as ex:
        # later I'd like to ignore this, but for now, let's see errors happen
        # raise ex
        pass

