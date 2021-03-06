import stripe
import settings
import requests
from common.functions import get_datetime
from common.stripemodels import *

import math
import logging; log = logging.getLogger('pd')

def stripe_create_card(profile, stripeToken):
    """
    Store the stripe.js token off into existing/new customer

    Return the card id
    """
    if not profile.stripe_customer_id:
        # Create a Customer on the pd account
        customer = stripe.Customer.create(
            card        = stripeToken,
            description = profile.email,
            api_key     = settings.STRIPE_SECRET_KEY, # out account!
            metadata    = {
                            'email':      profile.email,
                            'profile_id': profile.id
                          }
        )
        profile.stripe_customer_id = customer.id
        profile.save()
        card = customer.cards['data'][0]
    else:
        # Already had a profile, this is a new card
        customer = stripe.Customer.retrieve(
                profile.stripe_customer_id,
                api_key = settings.STRIPE_SECRET_KEY) # out account!
        card = customer.cards.create( card = stripeToken )

    return card.id

def stripe_set_default_card(profile, card_id):
    # Make sure they have a customer id
    if not profile.stripe_customer_id:
        log.error("%s does not have a stripe_customer_id! Can't save card %s!" % \
                    (profile.email, card_id))
        raise Exception(profile.email, card_id)
    else:
        # Retrieve the Customer
        cu = stripe.Customer.retrieve(
                profile.stripe_customer_id,
                api_key = settings.STRIPE_SECRET_KEY) # out account!

        # Set the default card
        cu.default_card = card_id
        cu.save()

def stripe_remove_charge(job):
    """
    Refund the (uncaptured) charge
    """
    if job.stripe_job.stripe_charge_id:
        ch = stripe.Charge.retrieve(
                job.stripe_job.stripe_charge_id,
                api_key=job.doctor.stripe_connect.access_token)
        ch.refunds.create()

        # leave cents and the card id so it can be charged later
        job.stripe_job.stripe_charge_id = ''
        job.stripe_job.save()
    else:
        # There's no charge to remove when the job is being refunded before a doctor
        # has ever taken the job
        log.info("Could not remove charge from job %s. No charge to remove." % job.id)

def calc_transfer_fees(cents):
    """
    The amount that stripe takes from a transaction. We decrease our cut
    to compensate for this, allowing doctors to receive what we said they'd receive.
    """
    return int(math.ceil(cents * 0.029)) + 30

def stripe_create_hold(job, doctor, doc_payout_price):
    """
    Create an uncaptured hold on a card.
    """
    pd_cut = job.stripe_job.cents                         \
             - doc_payout_price                           \
             - calc_transfer_fees(job.stripe_job.cents)

    # First, we have to retrieve the customer from the pd account and
    # create a token with which we'll charge them on the doctor's account
    charge_token = stripe.Token.create(
        customer = job.skaa.stripe_customer_id,
        card     = job.stripe_job.stripe_card_id, # card they chose in set_price
        api_key  = doctor.stripe_connect.access_token,
    )

    charge = stripe.Charge.create(
        amount      = job.stripe_job.cents, # amount they chose in set_price
        currency    = "usd",
        card        = charge_token, # card they chose in set_price
        description = "Charge for %s on job %d" % (job.skaa.email, job.id),
        metadata    = {
                        'user_email':      job.skaa.email,
                        'user_profile_id': job.skaa.id,
                        'doc_email':       doctor.email,
                        'doc_profile_id':  doctor.id,
                      },
        capture     = False, # Not captured yet!
        api_key     = doctor.stripe_connect.access_token,
        statement_description = "(PicDoctors)",
        application_fee       = pd_cut,
    )
    job.stripe_job.stripe_charge_id = charge.id
    job.stripe_job.hold_date = get_datetime()
    job.stripe_job.save()

def stripe_capture_hold(job):
    """
    Actually charge the person who we had previously placed the hold on

    This can throw an error.
    """
    then = job.stripe_job.hold_date 
    now  = get_datetime()
    if(now - then).days >= 6:
        log.info("Job %d may have an expired hold, let's recreate it. (now = [%s], then=[%s]" \
                % (job.id, now.__str__(), then.__str__()))
        stripe_create_hold(job, job.doctor, job.payout_price_cents)

    ch = stripe.Charge.retrieve(
            job.stripe_job.stripe_charge_id,
            api_key = job.doctor.stripe_connect.access_token,
            )
    ch.capture()
    job.stripe_job.captured_date = get_datetime()
    job.save()

def stripe_get_credit_cards(profile):
    """
    Retrieve a list of credit cards associated with a user
    """
    if profile.stripe_customer_id:
        struct = stripe.Customer.retrieve(
                profile.stripe_customer_id,
                api_key=settings.STRIPE_SECRET_KEY).cards.all(limit=40)
        all_cards = [card for card in struct['data']]
        ret = []

        # CRAZY HACK FOR GEORGE KENNEDY, 7-21-2014
        # Using company cc to pay for his job without leaving it 'listed'
        # TODO -- REMOVE THIS
        for card in all_cards:
            if card.last4 == '2921' and card.exp_month == 3 and card.exp_year == 2016:
                pass
            else:
                ret.append(card)

        return ret
    else:
        return []

def stripe_delete_credit_card(profile, card_id):
    """
    Delete a given card from a user's stripe profile

    Return True for success, False for failure
    """
    ret = False
    try:
        if profile.stripe_customer_id:
            customer = stripe.Customer.retrieve( profile.stripe_customer_id,
                                                 api_key = settings.STRIPE_SECRET_KEY )
            response = customer.cards.retrieve(card_id).delete()
            ret = response['deleted']
    except Exception as e:
        log.error("Could not delete card %s for %s: %s" % \
                   (card_id, profile.email, e.message))
    return ret

def stripe_validate_card_works(card_id, album, profile):
    """
    Create an *uncaptured* charge of $1 and immediately release that
    charge. This makes sure that the card actually works.

    We've had a number of people leave bad cards attached to a job, which
    we don't catch until a doctor tries to start on the job. We'd rather
    do basic sanity on the card while they are creating the job.
    """

    # See if we can place a hold for $1
    charge = stripe.Charge.create(
        amount      = 50, # a $1.00 charge
        currency    = "usd",
        card        = card_id,
        description = "Card validation. Uncaptured charge! Album %s -- %s" % \
                      (album.id, album.userprofile.email),
        metadata    = {
                        'user_email':      album.userprofile.email,
                        'user_profile_id': album.userprofile.id,
                      },
        capture     = False, # Not captured yet!
        api_key     = settings.STRIPE_SECRET_KEY, # out account!
        statement_description = "(PicDoctors)",
        customer    = profile.stripe_customer_id,
    )

    # Immediately release it
    charge.refunds.create()


def get_stripe_access_token_response(code):
    url = settings.STRIPE_CONNECT_SITE + settings.STRIPE_CONNECT_TOKEN
    data = {
       'grant_type':    'authorization_code',
       'client_id':     settings.STRIPE_CLIENT_ID,
       'client_secret': settings.STRIPE_SECRET_KEY,
       'code':          code
       }
    resp = requests.post(url, params=data)

    # Grab access_token (use this as your user's API key)
    return resp

def connect_stripe_connect_account(profile, json):
    if json.get('token_type') and json.get('access_token'):
        s = StripeConnect()
        s.token_type             = json.get('token_type')
        s.stripe_publishable_key = json.get('stripe_publishable_key')
        s.scope                  = json.get('scope')
        s.livemode               = json.get('livemode')
        s.stripe_user_id         = json.get('stripe_user_id')
        s.refresh_token          = json.get('refresh_token')
        s.access_token           = json.get('access_token')
        s.save()
        profile.stripe_connect = s
        profile.save()
