from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from annoying.functions import get_object_or_None
from annoying.decorators import render_to

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

# So, this is a view, but I'm putting it in here cause it seems
# way to small to put in it's own file. Sue me.
@render_to('permission_denied.html')
def permission_denied(request):
    return {}

