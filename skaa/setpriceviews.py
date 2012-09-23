# Create your views here.
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.core.urlresolvers import reverse
from django.views.decorators.csrf import csrf_protect
from django.utils import simplejson
from django.http import HttpResponse

from annoying.decorators import render_to

from skaa.uploadviews import get_batch_id
from common.models import Pic
from common.models import Batch
from common.models import Group
from common.models import ungroupedId
from models import Markup

import stripe

import pdb
import logging

# Require at least $2.00 for each output picture
min_price_per_picgroup = 2.0

# test key! use real key in production
stripe.api_key = 'sk_whv5t7wgdlPz1YTZ8mGWpXiD4C8Ag'

# TODO - require used to be logged in to even use this
@render_to('set_price.html')
def set_price(request):
    batch = Batch.objects.get( pk=get_batch_id(request) )

    if not batch or batch.num_groups == 0:
        # Hm, how did they get here? Strange. Send them to upload.
        return redirect('upload')

    min_price = min_price_per_picgroup * batch.num_groups
    if request.method == 'GET':
        pass
    elif request.method == 'POST':
        # get the credit card details submitted by the form
        token = request.POST['stripeToken']

        # We want whole cents. Convert string to float, multiply by 100,
        # and then convert to int (which floors any remaining fractional digits)
        price = int(float(request.POST['price'])*100)
        # TODO -- make sure above value works, is a valid string, etc

        # create the charge on Stripe's servers - this will charge the user's card
        charge = stripe.Charge.create(
            amount=price, # amount in cents, again
            currency="usd",
            card=token,
            description="payinguser@example.com"
        )

    return { 'min_price' : min_price }


