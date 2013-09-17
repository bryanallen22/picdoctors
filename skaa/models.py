from django.db import models

from common.models import DeleteMixin
from common.models import Pic

################################################################################
# Markup
#
# Stuff that the user says should change about their picture
################################################################################
class Markup(DeleteMixin):
    pic         = models.ForeignKey(Pic)

    ######
    # These should match the backbone.js model (see markup.js)
    ######
    left         = models.IntegerField(blank=False)
    top          = models.IntegerField(blank=False)
    width        = models.IntegerField(blank=False)
    height       = models.IntegerField(blank=False)
    description  = models.TextField(blank=True)

