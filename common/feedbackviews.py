from annoying.decorators import ajax_request
from common.functions import get_profile_or_None
from django.utils import simplejson
from emailer.emailfunctions import send_email

@ajax_request
def feedback(request):
    data = simplejson.loads(request.body)
    profile = get_profile_or_None(request)

    if profile:
        from_whom = profile.email
        logged_in = True
    else:
        from_whom = data['from_whom'].strip() or 'Cowardly Lion'
        logged_in = False
        
    feedback = data['user_feedback'].strip()
    success = False

    if feedback != '':
        success = send_email(request=request,
                             email_address='feedback@picdoctors.com',
                             template_name='feedback_email.html',
                             template_args={'from'      : from_whom,
                                            'feedback'  : feedback,
                                            'logged_in' : logged_in },
                            )
        
    return { 'success': success }

