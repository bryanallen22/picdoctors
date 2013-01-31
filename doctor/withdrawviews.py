# Create your views here.
from django.contrib.auth.decorators import login_required
from django.utils import simplejson
from django.http import HttpResponse
from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from django.contrib.humanize.templatetags.humanize import intcomma

from annoying.decorators import render_to

from common.functions import get_profile_or_None, get_or_create_balanced_account
from common.models import BPAccountWrapper

import balanced
import settings

#register = template.Library()

@login_required
@render_to('withdraw.html')
def withdraw(request):
    profile = get_profile_or_None(request)
    account = get_or_create_balanced_account(request, profile)

    if request.method == "GET":
        return {
            'balance' : 5.00,
        }
    elif request.method == "POST":
        return {}

