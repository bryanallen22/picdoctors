# This file should encompass all calls, models, etc required for balanced.

from common.basemodels import *
from common.models import *

from django.db import models

import logging

import balanced
import settings

import ipdb
ipdb.set_trace()
#balanced.configure(settings.BALANCED_API_KEY_SECRET)

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
    ipdb.set_trace()
    acct = profile.bp_account_wrapper.fetch()

    #acct.debit(
    #    appears_on_statement_as='PicDoctors',
    #    amount=job.,
    #    description='Some descriptive text for the debit in the dashboard',
    #)


################################################################################
# Credit stuff
################################################################################

