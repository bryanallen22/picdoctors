import stripe
import settings
import requests
from common.functions import get_datetime
from common.stripemodels import *

import logging; log = logging.getLogger('pd')

def stripe_create_card(profile, stripeToken):
    """
    Store the stripe.js token off into existing/new customer

    Return the card id
    """
    if not profile.stripe_customer_id:
        # Create a Customer
        customer = stripe.Customer.create(
            card        = stripeToken,
            description = profile.email,
            api_key     = settings.STRIPE_SECRET_KEY
        )
        profile.stripe_customer_id = customer.id
        profile.save()
        card = customer.cards['data'][0]
    else:
        # Already had a profile, this is a new card
        customer = stripe.Customer.retrieve(
                profile.stripe_customer_id,
                api_key = settings.STRIPE_SECRET_KEY)
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
                api_key = settings.STRIPE_SECRET_KEY)

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
                api_key=settings.STRIPE_SECRET_KEY)
        ch.refunds.create()
    else:
        log.error("Could not remove charge from job %s -- stripe_charge_id isn't set!" % job.id)

    # leave cents and the card id so it can be charged later
    job.stripe_job.stripe_charge_id = ''
    job.stripe_job.save()

def stripe_capture_hold(job):
    """
    Actually charge the person who we had previously placed the hold on

    This can throw an error.
    """
    ch = stripe.Charge.retrieve(job.stripe_job.stripe_charge_id)
    ch.capture()
    job.stripe_job.charge_date = get_datetime()
    job.save()

def stripe_get_credit_cards(profile):
    """
    Retrieve a list of credit cards associated with a user
    """
    if profile.stripe_customer_id:
        struct = stripe.Customer.retrieve(
                profile.stripe_customer_id,
                api_key=settings.STRIPE_SECRET_KEY).cards.all(limit=40)
        return [card for card in struct['data']]
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
    except Exception, e:
        log.error("Could not delete card %s for %s: %s" % \
                   (card_id, profile.email, e.message))
    return ret




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
