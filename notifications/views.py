# Create your views here.

from common.functions import get_profile_or_None
from annoying.functions import get_object_or_None
from django.shortcuts import redirect



#markup page when we don't specify a album_id (get it from request)
@login_required
def notification_redirecter(request, notification_id):
    notification = get_object_or_None(id=notification_id)
    profile = get_profile_or_None(request)
    if not notification or not profile:
        redirect('/')

    if profile == notification.recipient:
        redirect(notification.url)

    redirect('/')


