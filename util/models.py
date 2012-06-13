from django.db import models
from django.contrib.auth.models import User

################################################################################
# UserProfile
#
#  Information about the user goes here. This table goes in conjuction with
#  the User table, which is managed by django
################################################################################
class UserProfile(models.Model):
    # This field is required.
    user = models.OneToOneField(User)

    # Other fields here
    accepted_eula = models.BooleanField()
    favorite_animal = models.CharField(max_length=20, default="Dragons.")
