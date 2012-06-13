from django.db import models

from util.models import DeleteMixin
from upload.models import Pic

################################################################################
# Markup
#
# Stuff that the user says should change about their picture
################################################################################
class Markup(DeleteMixin):
    pic         = models.ForeignKey(Pic)

    created     = models.DateField(auto_now_add=True)
    # Leave     room for various patterns: '#049CDB' such as 'rgb(100, 100, 100)'
    left        = models.IntegerField(blank=False)
    top         = models.IntegerField(blank=False)
    width       = models.IntegerField(blank=False)
    height      = models.IntegerField(blank=False)
    description = models.TextField(blank=True)

