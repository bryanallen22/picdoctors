# Create your views here.
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.utils import simplejson

from annoying.decorators import render_to

from common.decorators import user_passes_test
from common.functions import get_unfinished_album
from common.models import Album
from common.models import Group
from common.models import Pic
from common.models import ungroupedId
from models import Markup
from skaa.jobsviews import create_job

import stripe

import pdb
import logging

# Require at least $2.00 for each output picture
min_price_per_pic = 2.0

# test key! use real key in production
stripe.api_key = 'sk_whv5t7wgdlPz1YTZ8mGWpXiD4C8Ag'

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
    # Strip away '$' and any commas. Boy, I sure hope people start giving
    # prices with commas (plural)!
    stripped = currency.replace('$','').replace(',','')

    # We want whole cents. Convert string to float, multiply by 100,
    # and then convert to int (which floors any remaining fractional digits)
    # This truncates -- does not round. Should be okay.
    price = int(float(stripped)*100)
    return price

@login_required
@render_to('set_price.html')
def set_price(request):
    invalid_price = False

    album, redirect_url = get_unfinished_album(request)
    if not album:
        return redirect(redirect_url)

    # We need valid sequences in this view. Set them. (This will fall through
    # if that's not necessary)
    album.set_sequences()

    min_price = min_price_per_pic * album.num_groups
    if request.method == 'GET':
        pass
    elif request.method == 'POST':
        # get the credit card details submitted by the form
        token = request.POST['stripeToken']

        # price is formatted as currency -- e.g. '$-1,234.56' or '$34.12'
        # convert it to cents and validate that it's an acceptable amount
        cents = currency_to_cents( request.POST['price'] );
        if (cents/100.0) >= min_price:
            # create the charge on Stripe's servers - this will charge the user's card
            charge = stripe.Charge.create(
                amount=cents, # amount in cents, again
                currency="usd",
                card=token,
                description=album.userprofile.user.username
            )
            album.finished = True
            album.save()
            create_job(request, album, charge)
            logging.info("Album owned by %s has been finished with price at $%s (cents)" %
                         (album.userprofile.user.username, cents))
            return redirect(reverse('job_page'))
        else:
            invalid_price = True

    str_min_price = "{0:.2f}".format(min_price)
    str_min_price_per_pic = "{0:.2f}".format(min_price_per_pic)
    return { 
        'min_price'         : str_min_price,
        'min_price_per_pic' : str_min_price_per_pic,
        'invalid_price'     : invalid_price,
    }


