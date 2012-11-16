from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from annoying.functions import get_object_or_None
import pdb

def get_or_define_group(name):
    g = get_object_or_None(Group, name=name)
    if not g:
        g = Group(name=name)
        g.save()
    return g

# we will crash on newdb, because Group doesn't exist to populate etc
# it's all cool, when you start the app it will run this code again
try:
    # Setup the Album Moderators (if it doesn't already exist)
    g = get_or_define_group('Album Moderators')

    # duplicate entries are ignored
    p = Permission.objects.get(codename='view_album')
    g.permissions.add(p)

    p = Permission.objects.get(codename='approve_album')
    g.permissions.add(p)
except:
    pass
