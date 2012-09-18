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
    created     = models.DateField(auto_now_add=True)

    ######
    # These should match the backbone.js model (see markup.js)
    ######
    left         = models.IntegerField(blank=False)
    top          = models.IntegerField(blank=False)
    width        = models.IntegerField(blank=False)
    height       = models.IntegerField(blank=False)
    # Leave room for various patterns: '#049CDB' such as 'rgb(100, 100, 100)'
    color        = models.CharField(max_length=32)
    # English name used to describe it to the user. ("What are the directions
    # for the deep purple with polka dots area")
    color_name   = models.CharField(max_length=64)
    # CSS border style: ex: 'dotted', 'dashed', 'solid'
    border_style = models.CharField(max_length=16)
    description  = models.TextField(blank=True)

