
from common.basemodels import *
from django.db import models

class StripeConnect(DeleteMixin):
    token_type = models.CharField(max_length=128, blank=True)
    stripe_publishable_key = models.CharField(max_length=128, blank=True)
    scope = models.CharField(max_length=128, blank=True)
    livemode = models.BooleanField(default=True)
    stripe_user_id = models.CharField(max_length=128, blank=True)
    refresh_token = models.CharField(max_length=128, blank=True)
    access_token = models.CharField(max_length=128, blank=True)
