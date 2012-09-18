
from django.db import models
from django.contrib import admin
from django.db.models.query import QuerySet
from django.core.exceptions import FieldError

################################################################################
# Some of this comes from:
#   http://stackoverflow.com/questions/809210/django-manager-chaining
# 
# Basically, we (most) all of our classes to be subclasses of DeleteMixin, so
# that instead of deleting objects, we simply mark them deleted. Good for
# recovering from bugs, etc.
################################################################################

################################################################################
# MixinManager
#
# Don't show deleted objects
################################################################################
class MixinManager(models.Manager):    
    def get_query_set(self):
        try:
            return self.model.MixinQuerySet(self.model).filter(deleted=False)
        except FieldError:
            return self.model.MixinQuerySet(self.model)


################################################################################
# BaseMixin
#
# Abstract class. Add things to admin, use MixinManager
################################################################################
class BaseMixin(models.Model):
    admin = models.Manager()
    objects = MixinManager()

    class MixinQuerySet(QuerySet):

        def globals(self):
            try:
                return self.filter(is_global=True)
            except FieldError:
                return self.all()

    class Meta:
        abstract = True


################################################################################
# DeleteMixin
#
# Most things should be a subclass of this. That way they delete by simply
# marking themselves deleted.
################################################################################
class DeleteMixin(BaseMixin):
    deleted = models.BooleanField(default=False)

    class Meta:
        abstract = True

    def delete(self):
        self.deleted = True
        self.save()


################################################################################
# GlobalMixin
#
# Globals, be a subclass of this. 'Nuff said.
################################################################################
class GlobalMixin(BaseMixin):
    is_global = models.BooleanField(default=True)

    class Meta:
        abstract = True


