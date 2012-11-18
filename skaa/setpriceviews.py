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

import pdb
import logging

import settings
import balanced

# the key is either 'test' or 'live' mode depending on 
balanced.configure(settings.BALANCED_API_KEY_SECRET)

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
    # Strip away '$' and any commas. Boy, I sure hope people start giving
    # prices with commas (plural)!
    stripped = currency.replace('$','').replace(',','')

    # We want whole cents. Convert string to float, multiply by 100,
    # and then convert to int (which floors any remaining fractional digits)
    # This truncates -- does not round. Should be okay.
    price = int(float(stripped)*100)
    return price

def create_charge_handler(request):
    """
    Save credit card info, create hold on card for the price they offer

    This is where we get credit card info (what we are allowed to have,
    at least)

    Returns:
        { "status" : 200, "next" : next_url } -- everything good
        { "status" : 402, "next" : "" }       -- less than min_price
    """
    if request.method != 'POST':
        return HttpResponse('[ ]', mimetype='application/json')

    ret = {
            "status"  : 200,
            "next"     : reverse('job_page'),
          }

    # price is formatted as currency -- e.g. '$-1,234.56' or '$34.12'
    # convert it to cents and validate that it's an acceptable amount
    cents = currency_to_cents( request.POST['price'] );
    if cents >= min_price * 100:
        # https://www.balancedpayments.com/docs/python/buyer#mobile-platforms
        # TODO - add card to account
        # TODO - actually do the 'hold'
        # TODO - change skaa/jobsviews 'generate_db_charge' and common/models 'Charge'
        album.finished = True
        album.save()
        create_job(request, album, charge)
        logging.info("Album owned by %s has been finished with price at $%s (cents)" %
                     (album.userprofile.user.username, cents))
        return redirect(reverse('job_page'))
    else:
        ret['status'] = 402 # Payment required
        ret['next'] = ''

    #return HttpResponse('[ ]', mimetype='application/json')
    response_data = simplejson.dumps(ret)
    return HttpResponse(response_data, mimetype='application/json')

@login_required
@render_to('set_price.html')
def set_price(request):
    album, redirect_url = get_unfinished_album(request)
    if not album:
        return redirect(redirect_url)

    # We need valid sequences in this view. Set them. (This will fall through
    # if that's not necessary)
    album.set_sequences()

    min_price = min_price_per_pic * album.num_groups
    if request.method == 'GET':
        pass
    str_min_price = "{0:.2f}".format(min_price)
    str_min_price_per_pic = "{0:.2f}".format(min_price_per_pic)
    str_num_pics = "%s" % album.num_groups
    return { 
        'marketplace_uri'   : settings.BALANCED_MARKETPLACE_URI,
        'min_price'         : str_min_price,
        'min_price_per_pic' : str_min_price_per_pic,
        'num_pics'          : str_num_pics,
        'DEBUG'             : settings.DEBUG,
    }


