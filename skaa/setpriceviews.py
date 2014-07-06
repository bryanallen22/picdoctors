# Create your views here.
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import redirect
from django.utils import simplejson

from annoying.decorators import render_to
from annoying.functions import get_object_or_None

from common.decorators import require_login_as
from common.functions import get_referer_view_and_id
from common.functions import get_unfinished_album
from common.models import Job, Album
from skaa.progressbarviews import get_progressbar_vars
from skaa.rejectviews import remove_previous_doctor
from emailer.emailfunctions import send_email
from skaa.jobsviews import create_job
from common.functions import get_profile_or_None, get_datetime
from common.stripefunctions import *


import logging; log = logging.getLogger('pd')

import stripe
import settings


# Require at least $2.00 for each output picture
min_price_per_pic = 2.0

def currency_to_cents(currency):
    """
    Input can by any currency formatting. Negative, '$', even (potentially)
    extra digits at the end. We need to turn that into cents.

    This is NOT the method that validates the price as okay

    Input example:
        '$-1,234.56'
    Output:
        -123456
    """

    if not currency:
        return 0

    # Strip away '$' and any commas. Boy, I sure hope people start giving
    # prices with commas (plural)!
    stripped = currency.replace('$','').replace(',','')

    # We want whole cents. Convert string to float, multiply by 100,
    # and then convert to int (which floors any remaining fractional digits)
    # This truncates -- does not round. Should be okay.
    price = int(float(stripped)*100)
    return price

@require_login_as(['skaa'])
def send_newjob_email(request, job):
    send_email(request,
               email_address=request.user.email,
               template_name='newjob_email.html',
               template_args={'jobs_url' : reverse( 'job_page' ),
                              'amount'   : job.stripe_job.cents, },
              )

@render_to('set_price.html')
def render_setprice(request, album, params=None):
    # We need valid sequences in this view. Set them. (This will fall through
    # if that's not necessary)
    album.set_sequences()

    profile = get_profile_or_None(request)

    user_credit_cards = stripe_get_credit_cards(profile)

    min_price = min_price_per_pic * album.num_groups
    if request.method == 'GET':
        pass
    str_min_price = "{0:.2f}".format(min_price)
    str_min_price_per_pic = "{0:.2f}".format(min_price_per_pic)

    ret = get_progressbar_vars(request, 'set_price')
    if params is not None:
        ret.update(params)
    ret.update({
        'STRIPE_PUBLISHABLE_KEY': settings.STRIPE_PUBLISHABLE_KEY,
        'min_price':              str_min_price,
        'min_price_per_pic':      str_min_price_per_pic,
        'num_pics':               album.num_groups,
        'credit_cards':           user_credit_cards,
        'album_id':               album.id,
    })
    return ret


@render_to('set_price.html')
def create_hold(request, album):
    """
    Save credit card info, create hold on card for the price they offer
    """
    ret = {}
    job = None

    profile = get_profile_or_None(request)

    min_price = min_price_per_pic * album.num_groups

    # price is formatted as currency -- e.g. '$-1,234.56' or '$34.12'
    # convert it to cents and validate that it's an acceptable amount
    try:
        cents = currency_to_cents( request.POST['price'] )
        if cents >= min_price * 100:

            if 'stripeToken' in request.POST:
                # This is a new card
                card_id = stripe_create_card(request.user, request.POST['stripeToken'])
            else:
                # Existing card. Let's set it to the default (though that's not necessary)
                card_id = request.POST['card_radio_group']
                stripe_set_default_card(request.user, card_id)

            sj = StripeJob(
                    stripe_card_id=card_id,
                    cents=cents)
            sj.save()

            # Don't make the Job until we (think) we're good on payments
            # (the card could still be declined later)
            if job is None:
                job = create_job(profile, album, sj)
            else:
                job.stripe_job = sj
                job.save()
            album.finished = True
            album.save()

            # TODO: get enough customers that this becomes spammy and has to be removed
            if settings.IS_PRODUCTION:
                send_email(
                    request=request,
                    email_address=['admin@picdoctors.com'],
                    template_name='tell_admins_hold_placed.html',
                    template_args={
                        'user_email_address': profile.email,
                        'cents':              cents,
                        'job':                job,
                    }
                )

            # Remove any previous doctor information, this essentially happens when they go from
            # refund to back in market
            remove_previous_doctor(job)

            send_newjob_email(request, job)

        else:
            # TODO - do I bother to display an error on the client? If they got here, it's probably
            # because they used a debugger to go under the client side min, and I don't feel any
            # particular need to be UI friendly to them. Perhaps I'll just ignore them?
            ret['serverside_error'] = 'You must pay at least $' + "{0:.2f}".format(min_price) + '.'
            return render_setprice(request, album, ret)
    except Exception as e:
        log.error("Error placing hold on album.id=%s! price=%s -- message=%s" % (album.id, request.POST['price'], e.message))
        ret['serverside_error'] = 'Uh oh, we failed to process your card. If this keeps happening, let us know.'
        return render_setprice(request, album, ret)

    return redirect (reverse('job_page'))

@require_login_as(['skaa'])
@render_to('set_price.html')
def increase_price(request, job_id):

    job = get_object_or_None(Job, id=job_id)
    profile = get_profile_or_None(request)

    if not job or not profile or job.skaa != profile:
        return redirect('/')

    user_credit_cards = stripe_get_credit_cards(profile)

    # Use float here -- /100 truncates, but /100. is cool
    original_price = (job.stripe_job.cents / 100.)
    min_price = original_price + 1
    str_min_price = "{0:.2f}".format(min_price)
    str_min_price_per_pic = "{0:.2f}".format(min_price_per_pic)
    str_num_pics = "%s" % job.album.num_groups
    str_original_price =  "{0:.2f}".format(original_price)

    ret = get_progressbar_vars(request, 'set_price')
    ret.update({
        'marketplace_uri'   : settings.BALANCED_MARKETPLACE_URI,
        'min_price'         : str_min_price,
        'min_price_per_pic' : str_min_price_per_pic,
        'num_pics'          : str_num_pics,
        'credit_cards'      : user_credit_cards,
        'increase_price'    : True,
        'original_price'    : str_original_price,
        'album_id'          : job.album.id,
    })
    return ret



@require_login_as(['skaa'])
@render_to('set_price.html')
def set_price(request, album_id=None):
    # On normal uploads, album should be None, but we retrieve it with get_unfinished_album
    # However, if comes from a job that was refunded and returned to the market, the album
    # can be passed in directly
    if album_id is None:
        album, redirect_url = get_unfinished_album(request)
        if not album:
            return redirect(redirect_url)
    else:
        album = get_object_or_None(Album, id=album_id)
        if not album:
            return redirect(reverse('upload'))
        if album.userprofile != request.user:
            return redirect(reverse('permission_denied'))

    if album.num_groups == 0:
        return redirect(reverse('upload'))

    if request.method == 'POST':
        return create_hold(request, album)
    elif request.method == 'GET':
        return render_setprice(request, album)

