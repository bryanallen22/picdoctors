# Create your views here.

from common.functions import get_profile_or_None, get_datetime
from annoying.functions import get_object_or_None
from django.shortcuts import redirect
from notifications.models import Notification, NotificationToIgnore
from django.utils import simplejson
from django.http import HttpResponse
from common.decorators import require_login_as
from annoying.decorators import ajax_request

import ipdb

#markup page when we don't specify a album_id (get it from request)
@require_login_as(['skaa', 'doctor'])
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

@ajax_request
@require_login_as(['skaa', 'doctor'])
def clear_notifications(request, notification_id):
    now = get_datetime()
    Notification.objects.filter(pk__lte=notification_id, recipient=request.user, viewed=False).update(viewed=True, updated=now)

    return {
        'ok': True
    }


@require_login_as(['skaa', 'doctor'])
def notification_handler(request):
    profile = get_profile_or_None(request)
    if request.method == 'POST' and profile:
        data = simplejson.loads(request.body)
        tp = data['type']
        ignore = not data['enabled']
        ignorers = NotificationToIgnore.objects.filter(profile=profile).filter(notification_type=tp)
        if len(ignorers) == 0:
            nti = NotificationToIgnore()
            nti.notification_type = tp
            nti.profile = profile
            nti.ignore = ignore
            nti.save()
        else:
            for nti in ignorers:
                nti.ignore = ignore
                nti.save()

    result = {}

    response_data = simplejson.dumps(result)
    return HttpResponse(response_data, mimetype='application/json')

