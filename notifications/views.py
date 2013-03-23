# Create your views here.

from common.functions import get_profile_or_None
from annoying.functions import get_object_or_None
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from notifications.models import Notification


#markup page when we don't specify a album_id (get it from request)
@login_required
def notification_redirecter(request, notification_id):
    notification = get_object_or_None(Notification, id=notification_id)
    profile = get_profile_or_None(request)
    if not notification or not profile:
        return redirect('/')

    if profile == notification.recipient:
        notification.viewed = True
        notification.save()
        return redirect(notification.url)

    return redirect('/')


