
from django.views.debug import SafeExceptionReporterFilter

from django.http import build_request_repr

# In short, we're subclassing the default filter for reporting exceptions
# so that we can change how it shows the 'request' object that it emails
# to us on errors. (We want it to show request.user.email).
# See more here: https://docs.djangoproject.com/en/1.6/howto/error-reporting/#custom-error-reports

class PicDoctorsExceptionReporterFilter(SafeExceptionReporterFilter):

    def get_request_repr(self, request):
        request_repr = build_request_repr(request, POST_override=self.get_post_parameters(request))

        user_email = "Unknown"
        if request.user.is_authenticated():
            user_email = request.user.email

        request_repr += "\nUser email: " + user_email
        return request_repr
