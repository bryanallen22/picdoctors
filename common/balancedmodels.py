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
# BPAccount
################################################################################
class BPAccount(DeleteMixin):
    """
    Balanced Payment Account - represents either a user or a doctor
    """
    uri = models.CharField(max_length=128, blank=True)

    def fetch(self):
        """
        Go get the object from Balanced. This is slow.
        """
        return balanced.Account.find(uri)

################################################################################
# BPHold
################################################################################
class BPHold(DeleteMixin):
    """
    Balanced Payment Hold - reserves money for up to 7 days
    """
    uri   = models.CharField(max_length=128, blank=True)

    # Cached info:
    cents = models.IntegerField(blank=False)

    def fetch(self):
        """
        Go get the object from Balanced. This is slow.
        """
        return balanced.Hold.find(uri)

################################################################################
# BPCredit
################################################################################
class BPCredit(DeleteMixin):
    """
    Balanced Payment Credit - ACH credit to doctor
    """
    uri   = models.CharField(max_length=128, blank=True)

    # Cached info:
    cents = models.IntegerField(blank=False)

    def fetch(self):
        """
        Go get the object from Balanced. This is slow.
        """
        return balanced.Credit.find(uri)

################################################################################
# BPDebit
################################################################################
class BPDebit(DeleteMixin):
    """
    Balanced Payment Debit - actual charge of a credit card
    """
    uri   = models.CharField(max_length=128, blank=True)

    # Cached info:
    cents             = models.IntegerField(blank=False)
    # Many debits can be associated with a single credit (saves $ on ACH transfer fee)
    associated_credit = models.ForeignKey(BPCredit, blank=True, null=True)

    def fetch(self):
        """
        Go get the object from Balanced. This is slow.
        """
        return balanced.Debit.find(uri)

