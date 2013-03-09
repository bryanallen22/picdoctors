from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from annoying.functions import get_object_or_None

def get_or_define_group(name):
    try:
        g = get_object_or_None(Group, name=name)
        if not g:
            g = Group(name=name)
            g.save()
        return g
    except:
        return None

def add_permission(group, name):
    try:
        p = Permission.objects.get(codename=name)
        group.permissions.add(p)
    except:
        pass
