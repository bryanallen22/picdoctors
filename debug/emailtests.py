from collections import namedtuple
from notifications.models import Notification

# Debug stuff

def send_test_emails(dst_email):
    """
    Send all of the various kinds of email to a given address. The purpose
    of this is to see the email content, since we're using nonstandard approaches
    to generating the emails (in some cases).

    This function makes heavy use of duck typing, faking lots of data types
    with namedtuple
    """

    # Fake feedback email
    from common.feedbackviews import send_feedback
    assert send_feedback(from_whom='bobson', feedback='This is a great site', to_email=dst_email)

    # Fake password reset
    from common.resetpasswordviews import reset_password
    from django.http.response import HttpResponse
    request = namedtuple("fakerequest", 'method, POST, META')
    request.method = 'POST'
    request.POST = { 'email' : dst_email }
    request.META = { }
    response = reset_password(request, email=dst_email)
    assert isinstance(response, HttpResponse)
    
    # Job price too low
    #from common.jobpricetoolowviews import send_user_email
    #fakejob = namedtuple('fakejob', 'id, skaa')
    #fakejob.id = 123456789 # only used to generate an (invalid) email link)
    #fakejob.skaa = namedtuple('fakejob_skaa', 'email')
    #fakejob.skaa.email = dst_email
    #send_user_email(fakejob)

    ## Notification email
    #from notifications.functions import send_email

