# Create your views here.
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.utils import simplejson

from annoying.decorators import render_to

from common.decorators import user_passes_test
from common.functions import get_unfinished_album
from common.functions import get_profile_or_None
from common.models import Album
from common.models import Group
from common.models import Pic
from common.models import ungroupedId
from common.models import BPAccountWrapper
from models import Markup
from skaa.jobsviews import create_job

import ipdb
import logging

import settings
import balanced


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

def create_or_get_balanced_account(profile, email_address, card_uri):
    """
    Create (or retrieve) a balanced account. Create card for the user if they
    don't already have it.
    """
    account = None
    if not profile.bp_account_wrapper:
        try:
            account = balanced.Marketplace.my_marketplace.create_buyer(email_address, card_uri)
            wrapper = BPAccountWrapper(uri=account.uri)
            wrapper.save()
            profile.bp_account_wrapper = wrapper
            profile.save()
            
        except balanced.exc.HTTPError as ex:
            if ex.category_code == 'duplicate-email-address':
                # So, Balanced already has an account associated with this email
                # address, but we don't have it saved under thir profile. Weird.
                #  1) We didn't save it, but we were supposed to. Why not?
                #  2) Some weird thing happened with changed emails? Or something? 
                #     Does that even make sense?
                #  3) you aren't in production and you keep wiping your db and adding 
                #     the same user
                if not settings.IS_PRODUCTION:
                    # In testlandia we just re link up user accounts with email addresses
                    # we know that there exists an account with this email address (hence the
                    # error)
                    account = balanced.Account.query.filter(email_address=email_address)[0]
                    # remove all our old cards associated with a pre-existing email_address
                    # at this point it's not like I can go back and uncreate our new card
                    for card in account.cards:
                        card.is_valid = False
                        card.save()

                    account.add_card(card_uri)
                    wrapper = BPAccountWrapper(uri=account.uri)
                    wrapper.save()
                    profile.bp_account_wrapper = wrapper
                    profile.save()
                else:
                    raise KeyError("Duplicate email address %s... this should have been saved under " \
                                   "profile.bp_account_wrapper..." % email_address)

                # bob@stuff.com registers, pays, saves cc
                #account = balanced.Account.query.filter(email_address=email_address)[0]
                #account.add_card(card_uri)
            else:
                # TODO: handle 400 or 409 errors
                raise
    else:
        account = balanced.Account.find( profile.bp_account_wrapper.uri )
        card = balanced.Card.find( card_uri )

        # As of 12/2012, card.account doesn't even exist. I can see them making it exist
        # later with 'None' as the value, though.
        if not hasattr(card, 'account') or not card.account:
            account.add_card( card_uri )
        elif card.account.uri != account.uri:
            raise KeyError("This card's account uri (%s) is already set, and does not match the "\
                           "current user account uri (%s)!" % (card.account.uri, account.uri))

    return account


def place_hold(album, user, cents, card_uri):
    """
    Do the actual 7 day hold associated with the album and user
    """
    email_address = user.email
    profile = user.get_profile()

    balanced.configure(settings.BALANCED_API_KEY_SECRET)

    account = create_or_get_balanced_account(profile, email_address, card_uri)

    # This creates a hold on the card. We are guaranteed that we can
    # actually debit this amount for up to 7 days from now.
    hold = account.hold(cents, meta={}, source_uri=card_uri,
                      appears_on_statement_as="PicDoctors.com")

    create_job(profile, album, hold)
    album.finished = True
    album.save()
    logging.info("Album owned by %s has been finished with price at $%s (cents)" %
                     (album.userprofile.user.username, cents))

def create_hold_handler(request):
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

    ret = {}
    album, _ = get_unfinished_album(request)
    min_price = min_price_per_pic * album.num_groups

    # price is formatted as currency -- e.g. '$-1,234.56' or '$34.12'
    # convert it to cents and validate that it's an acceptable amount
    cents = currency_to_cents( request.POST['price'] )

    if cents >= min_price * 100:

        place_hold(album, request.user, cents, request.POST['card_uri'])

        ret['status'] = 200
        ret['next'] = reverse('job_page')

    else:
        # TODO - do I bother to display an error on the client? If they got here, it's probably
        # because they used a debugger to go under the client side min, and I don't feel any
        # particular need to be UI friendly to them. Perhaps I'll just ignore them?
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
    if album.num_groups == 0:
        return redirect(reverse('upload'))

    # We need valid sequences in this view. Set them. (This will fall through
    # if that's not necessary)
    album.set_sequences()

    profile = get_profile_or_None(request)
    
    balanced.configure(settings.BALANCED_API_KEY_SECRET)

    if profile.bp_account_wrapper:
        # Get the balanced account info. This is slow.
        acct = balanced.Account.find( profile.bp_account_wrapper.uri )

        user_credit_cards = [c for c in acct.cards if c.is_valid]
    else:
        user_credit_cards = []

    # card.brand = 'Visa'
    # card.last_four = '1234'
    # card.expiration_month
    # card.expiration_year

    min_price = min_price_per_pic * album.num_groups
    if request.method == 'GET':
        pass
    str_min_price = "{0:.2f}".format(min_price)
    str_min_price_per_pic = "{0:.2f}".format(min_price_per_pic)
    str_num_pics = "%s" % album.num_groups

    return { 
        'marketplace_uri'   : settings.BALANCED_MARKETPLACE_URI,
        'IS_PRODUCTION'     : settings.IS_PRODUCTION,
        'min_price'         : str_min_price,
        'min_price_per_pic' : str_min_price_per_pic,
        'num_pics'          : str_num_pics,
        'credit_cards'      : user_credit_cards,
    }


