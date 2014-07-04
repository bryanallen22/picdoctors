# Create your views here.

from django.shortcuts import redirect
from django.contrib.auth import authenticate, login, logout

from annoying.decorators import render_to

from common.decorators import require_login_as
from common.models import *

@require_login_as(['admin'])
@render_to("loginas.html")
def loginas(request):
    """
    Log in as another user.

    BE VERY CAREFUL. But useful for helping inept users.
    """
    if request.method == "GET":
        return {
            'error' : '',
        }
    if request.method == "POST":
        login_as_email = request.POST['login_email']

        matches = Profile.objects.filter(email=login_as_email)
        if matches.count() > 1:
            error = "WTF I found 2 users with that email!?"

        elif matches.count() == 1:
            account = matches[0]
            if account.is_active:
                # This next line cheats us into being able to login as the user
                # without actually authenticating. Kids, don't try this at home.
                account.backend = 'django.contrib.auth.backends.ModelBackend'
                login(request, account)
                request.session.set_expiry(120) # you get 2 minutes, man. Make the best of it.
                return redirect('/')
            else:
                error = "Account is inactive"

        else:
            error = "Couldn't find that user. I thought I told you to be careful."

        return {
            'error' : error,
        }
