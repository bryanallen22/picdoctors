from common.permissionfunctions import get_or_define_group, add_permission
import ipdb

# we will crash on newdb, because Group doesn't exist to populate etc
# it's all cool, when you start the app it will run this code again
# Setup the Album Moderators (if it doesn't already exist)
g = get_or_define_group('Album Moderators')

add_permission(g, 'album_approver')

g = get_or_define_group('PD Permissions')

add_permission(g, 'admin')
add_permission(g, 'doctor')
add_permission(g, 'skaa')

