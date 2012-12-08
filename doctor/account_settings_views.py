# Create your views here.
from django.contrib.auth.decorators import login_required

from annoying.decorators import render_to

@login_required
@render_to('account_settings_doc.html')
def settings_doc(request):
    return {}

