import stripe
import settings

from common.functions import get_datetime

import logging; log = logging.getLogger('pd')

def stripe_place_hold_newcard(profile, cents, stripeToken):
    """
    Place a charge, but don't capture it yet. (Good for up to 7 days.)
    """
    ret = None
    stripe.api_key = settings.STRIPE_SECRET_KEY

    if not profile.stripe_customer_id:
        # Create a Customer
        customer = stripe.Customer.create(
            card=stripeToken,
            description=profile.email,
        )
        profile.stripe_customer_id = customer.id
        profile.save()

    # Create the charge on Stripe's servers - this will charge the user's card
    try:
        # Charge the Customer instead of the card
        charge = stripe.Charge.create(
            amount=cents,
            currency="usd",
            customer=profile.stripe_customer_id,
            description='%s' % profile.email,
            capture=False, # don't charge them yet!
        )
        ret = charge.id
    except stripe.CardError, e:
      # The card has been declined
      log.error("%s has had their card declined for %d cents" % \
                 (profile.email, cents))
      ret = None

    return ret

def stripe_place_hold_existingcard(profile, cents, card_id):
    """
    Update customer's default card and place a charge,
    but don't capture it yet. (Good for up to 7 days.)

    I wish I knew how to charge a card without updating
    the default, but I don't. The normal API to create
    a charge takes a 'card' param, but it wants a token
    from stripe.js

    This may raise an error. You gotta deal with it
    """
    ret = None
    stripe.api_key = settings.STRIPE_SECRET_KEY

    # Make sure they have a customer id
    if not profile.stripe_customer_id:
        return None

    # Make sure this card belongs to them
    cards_struct = stripe.Customer.retrieve(profile.stripe_customer_id).cards.all(limit=100)
    cards = [card.id for card in cards_struct['data']]
    if card_id not in cards:
        return None

    # Set the default card
    cu = stripe.Customer.retrieve(profile.stripe_customer_id)
    cu.default_card = card_id
    cu.save()

    # Create the charge on Stripe's servers - this will charge the user's card
    try:
        # Charge the Customer instead of the card
        charge = stripe.Charge.create(
            amount=cents,
            currency="usd",
            customer=profile.stripe_customer_id,
            description='%s' % profile.email,
            capture=False, # don't charge them yet!
        )
        ret = charge.id
    except stripe.CardError, e:
      # The card has been declined
      log.error("%s has had their card declined for %d cents" % \
                 (profile.email, cents))
      ret = None

    return ret


def stripe_remove_charge(job):
    ch = stripe.Charge.retrieve(job.stripe_charge_id)
    ch.refunds.create()
    job.stripe_charge_id = ''
    job.stripe_charge_date = None
    job.stripe_cents = -1

def stripe_capture_hold(job):
    """
    Actually charge the person who we had previously placed the hold on

    This can throw an error.
    """
    stripe.api_key = settings.STRIPE_SECRET_KEY

    ch = stripe.Charge.retrieve(job.stripe_charge_id)
    if ch.refunded:
        log.info("job %d has already refunded charge %d, trying to create a new one") % (job.id, job.stripe_charge_id)
        # Charge the Customer instead of the card
        charge = stripe.Charge.create(
            amount=ch.amount,
            currency="usd",
            customer=job.skaa.stripe_customer_id,
            description='%s charge for job %d' % (profile.email, job.id),
            capture=True,
        )
        job.stripe_charge_id = charge.id
        job.stripe_charge_date = get_datetime()
        job.stripe_cents = ch.amount
        job.save()
    else:
        ch.capture()

def stripe_get_credit_cards(profile):
    """
    Retrieve a list of credit cards associated with a user
    """
    stripe.api_key = settings.STRIPE_SECRET_KEY
    if profile.stripe_customer_id:
        struct = stripe.Customer.retrieve(profile.stripe_customer_id).cards.all(limit=20)
        return [card for card in struct['data']]
    else:
        return []
