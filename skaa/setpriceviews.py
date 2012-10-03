# Create your views here.
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.core.urlresolvers import reverse
from django.views.decorators.csrf import csrf_protect
from django.utils import simplejson
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

from annoying.decorators import render_to

from common.models import Pic
from common.models import Batch
from common.models import Group
from common.models import ungroupedId
from common.decorators import user_passes_test
from skaa.jobsviews import create_job
from models import Markup

import stripe

import pdb
import logging

# Require at least $2.00 for each output picture
min_price_per_pic = 2.0

# test key! use real key in production
stripe.api_key = 'sk_whv5t7wgdlPz1YTZ8mGWpXiD4C8Ag'

def set_price_test(request):
    if Batch.get_unfinished(request):
        return True
    return False

@login_required
@user_passes_test(test_fcn=set_price_test, redirect_name='upload')
@render_to('set_price.html')
def set_price(request):
    batch = Batch.get_unfinished(request)
    min_price = min_price_per_pic * batch.num_groups
    if request.method == 'GET':
        pass
    elif request.method == 'POST':
        # get the credit card details submitted by the form
        token = request.POST['stripeToken']

        # We want whole cents. Convert string to float, multiply by 100,
        # and then convert to int (which floors any remaining fractional digits)
        price = int(float(request.POST['price'])*100)
        # TODO -- make sure above value works, is a valid string, and isn't below the minimum price

        # create the charge on Stripe's servers - this will charge the user's card
        charge = stripe.Charge.create(
            amount=price, # amount in cents, again
            currency="usd",
            card=token,
            description=batch.userprofile.user.username
        )
        batch.finished = True
        batch.save()
        create_job(request, batch, price) # price is in cents
        logging.info("Batch owned by %s has been finished with price at $%s" %
                     (batch.userprofile.user.username, price))
        return redirect(reverse('job_page'))

    str_min_price = "{0:.2f}".format(min_price)
    str_min_price_per_pic = "{0:.2f}".format(min_price_per_pic)
    return { 
        'min_price' :          str_min_price,
        'min_price_per_pic' :  str_min_price_per_pic,
    }


