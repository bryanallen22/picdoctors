
from common.basemodels import *
from django.db import models

class StripeConnect(DeleteMixin):
    token_type             = models.CharField(max_length=128, blank=True)
    stripe_publishable_key = models.CharField(max_length=128, blank=True)
    scope                  = models.CharField(max_length=128, blank=True)
    livemode               = models.BooleanField(default=True)
    stripe_user_id         = models.CharField(max_length=128, blank=True)
    refresh_token          = models.CharField(max_length=128, blank=True)
    access_token           = models.CharField(max_length=128, blank=True)

class StripeJob(DeleteMixin):
    """
    Stripe information to be associated with each job. Maps 1:1 with Job,
    but kept separate to keep it clean
    """
    ###### Set once the user creates the Job:
    # Which card did they use for this job?
    stripe_card_id         = models.CharField(max_length=128, blank=False)
    cents                  = models.IntegerField(default=-1, blank=False)

    ###### Set once a doctor applies for the job:
    stripe_charge_id       = models.CharField(max_length=128, blank=True)
    hold_date              = models.DateTimeField(blank=True, null=True)

    ###### Set once user accepts job and charge is captured:
    captured_date     = models.DateTimeField(blank=True, null=True)

