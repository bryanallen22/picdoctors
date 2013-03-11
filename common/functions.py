
from django.core.exceptions import MultipleObjectsReturned
from django.core.urlresolvers import reverse
from django.views.decorators.csrf import csrf_exempt
from annoying.functions import get_object_or_None

from common.models import Album

import logging
import urllib
import urlparse

from datetime import datetime, timedelta
import pytz
from django.utils.timezone import utc

import re
import os

import ipdb

def get_profile_or_None(request):
    """ Get the request user profile if they are logged in """
    if request.user.is_authenticated():
        return request.user
    return None

def get_datetime():
    return datetime.utcnow().replace(tzinfo=utc)

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
    now = get_datetime()
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


def get_referer_view_and_id(request, default=None):

    # if the user typed the url directly in the browser's address bar
    referer = request.META.get('HTTP_REFERER')
    if not referer:
        return default

    # remove the protocol and split the url at the slashes
    referer = re.sub('^https?:\/\/', '', referer).split('/')
    if referer[0] != request.META.get('HTTP_HOST'):
        return default

    if len(referer) > 2:
        return referer[1], referer[2]

    return default

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

        which_user = user.email
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

