from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db import transaction, DatabaseError

from annoying.functions import get_object_or_None
from annoying.decorators import render_to
from south.signals import post_migrate

import logging; log = logging.getLogger('pd')

def get_or_define_group(name):
    log.info('get_or_define_group: name=%s' % name)
    try:
        g = get_object_or_None(Group, name=name)
        if not g:
            g = Group(name=name)
            g.save()
        return g
    except DatabaseError:
        log.error('get_or_define_group: DatabaseError!')
        # Postgres gets cranky if you don't do this
        transaction.rollback()
    except:
        log.error('get_or_define_group: Some other exception!')
        return None
    log.info('Returning from get_or_define_group')

def add_permission(group, name):
    try:
        p = Permission.objects.get(codename=name)
        group.permissions.add(p)
    except DatabaseError:
        # Postgres gets cranky if you don't do this
        transaction.rollback()
    except:
        pass

# So, this is a view, but I'm putting it in here cause it seems
# way to small to put in it's own file. Sue me.
@render_to('permission_denied.html')
def permission_denied(request):
    return {}

def create_groups_and_permissions(sender, **kwargs):
    """
    Set up moderators, groups, permissions
    """
    log.info('running create_groups_and_permissions')

    # Setup the Album Moderators (if it doesn't already exist)
    g = get_or_define_group('Album Moderators')

    add_permission(g, 'album_approver')

    g = get_or_define_group('PD Permissions')

    add_permission(g, 'admin')
    add_permission(g, 'doctor')
    add_permission(g, 'skaa')

post_migrate.connect(create_groups_and_permissions)

