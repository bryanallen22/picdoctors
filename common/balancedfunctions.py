# This file should encompass all calls, models, etc required for balanced.

from common.basemodels import *
from common.models import *

from django.db import models

import logging

import balanced
import settings

import ipdb
#ipdb.set_trace()

from skaa.jobsviews import create_job

################################################################################
# Accounts stuff
################################################################################
def get_buyer_account(profile, email_address, card_uri):
    """
    Create (or retrieve) a balanced account. Create card for the user if they
    don't already have it.
    """
    account = None
    balanced.configure(settings.BALANCED_API_KEY_SECRET)
    if not profile.bp_account:
        try:
            account = balanced.Marketplace.my_marketplace.create_buyer(email_address, card_uri)
            wrapper = BPAccount(uri=account.uri)
            wrapper.save()
            profile.bp_account = wrapper
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
                    wrapper = BPAccount(uri=account.uri)
                    wrapper.save()
                    profile.bp_account = wrapper
                    profile.save()
                else:
                    raise KeyError("Duplicate email address %s... this should have been saved under " \
                                   "profile.bp_account..." % email_address)

                # bob@stuff.com registers, pays, saves cc
                #account = balanced.Account.query.filter(email_address=email_address)[0]
                #account.add_card(card_uri)
            else:
                # TODO: handle 400 or 409 errors
                raise
    else:
        account = profile.bp_account.fetch()
        card = balanced.Card.find( card_uri )

        # As of 12/2012, card.account doesn't even exist. I can see them making it exist
        # later with 'None' as the value, though.
        if not hasattr(card, 'account') or not card.account:
            account.add_card( card_uri )
        elif card.account.uri != account.uri:
            raise KeyError("This card's account uri (%s) is already set, and does not match the "\
                           "current user account uri (%s)!" % (card.account.uri, account.uri))

    return account

def get_merchant_account(request, profile=None):
    # Configure balanced
    balanced.configure(settings.BALANCED_API_KEY_SECRET)
    if not profile:
        profile = get_profile_or_None(request)

    # Get their account if they have one
    if profile.bp_account:
        account = profile.bp_account.fetch()
    else:
        # Create a new account and associate it with this profile
        account = balanced.Account().save()
        try:
            account.email_address = request.user.email
            account.save()
        except balanced.exc.HTTPError as ex:
            if ex.category_code == 'duplicate-email-address':
                if not settings.IS_PRODUCTION:
                    # only in non production will we take control. See similar
                    # comments above in get_buyer_account
                    account = balanced.Account.query.filter(email_address=request.user.email)[0]
                    # TODO - invalidate existing things on this account?
                else:
                    raise KeyError("Duplicate email address %s... this should have been saved under " \
                                   "profile.bp_account..." % email_address)
        wrapper = BPAccount(uri=account.uri)
        wrapper.save()
        profile.bp_account = wrapper
        profile.save()

    return account

def is_merchant(account):
    """
    Checks to see if this person is a merchant. 'account' is a fetched balanced
    payment account
    """
    if 'merchant' in account.roles:
        return True
    return False

################################################################################
# Bank Account stuff
################################################################################

################################################################################
# Credit Card stuff
################################################################################

################################################################################
# Hold stuff
################################################################################
def place_hold(job, album, user, cents, card_uri):
    """
    Do the actual 7 day hold associated with the album and user
    """
    balanced.configure(settings.BALANCED_API_KEY_SECRET)
    email_address = user.email
    profile = user.get_profile()

    account = get_buyer_account(profile, email_address, card_uri)

    # This creates a hold on the card. We are guaranteed that we can
    # actually debit this amount for up to 7 days from now.
    hold = account.hold(cents, meta={}, source_uri=card_uri,
                      appears_on_statement_as="PicDoctors.com")

    if job:
        update_job_hold(job, hold)
    else:
        create_job(profile, album, hold)

    album.finished = True
    album.save()
    logging.info("Album owned by %s has been finished with price at $%s (cents)" %
                     (album.userprofile.user.username, cents))


################################################################################
# Debit stuff
################################################################################
def do_debit(request, profile, job):
    # get the balanced account wrapper
    balanced.configure(settings.BALANCED_API_KEY_SECRET)
    user_acct = profile.bp_account.fetch()
    doc_acct = job.doctor.bp_account.fetch()

    if not is_merchant(doc_acct):
        raise KeyError("Doctors %s does not have a merchant balanced role" % job.doctor.user.email)

    debit = user_acct.debit(
        amount                  = job.bp_hold.cents,
        description             = 'Some descriptive text for the debit in the dashboard',
        hold_uri                = job.bp_hold.uri,
        merchant_uri            = doc_acct.uri,
        appears_on_statement_as = 'PicDoctors',
    )

    # Create a wrapper in our local db
    bp_debit = BPDebit(uri=debit.uri, associated_hold=job.bp_hold)
    bp_debit.save()
    job.bp_debit = bp_debit
    job.save()


################################################################################
# Credit stuff
################################################################################
def get_withdraw_jobs(doc_profile):
    """
    Get jobs that are available for withdrawal for a given doctor.
    """

    # This could be slow some day if a doctor has a bajillion jobs, we'd hate
    # to pull them all into memory just to find the unfinished ones, but I can't
    # figure out a way to do both steps at once
    jobs = Job.objects.filter(doctor=doc_profile, approved=True)

    return [job for job in jobs if job.bp_debit.associated_credit is None]

def credit_doctor(doc_profile):
    """
    Fully credit the doctor for all unpaid jobs
    """
    withdraw_jobs = get_withdraw_jobs(doc_profile)
    account = doc_profile.bp_account.fetch()
    bank_accounts = [ba for ba in account.bank_accounts if ba.is_valid]
    transfer_account = bank_accounts[0]

    total = 0
    for job in withdraw_jobs:
        total += job.payout_price_cents

    credit = transfer_account.credit( total )
    bp_credit = BPCredit( uri=credit.uri, cents=total )
    bp_credit.save()

    for job in withdraw_jobs:
        job.bp_debit.associated_credit = bp_credit
        job.bp_debit.save()

    return total
