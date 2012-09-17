from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.core.urlresolvers import reverse
from django.http import HttpResponse

from annoying.decorators import render_to

from skaa.uploadviews import get_batch_id
from common.models import Batch

import pdb
import logging

@render_to('signin.html')
def signin(request):
    ret = {
        'bad_email_or_password' : False,
        'passwords_didnt_match' : False,
    }

    if request.method == 'GET':
        pass

    elif request.method == 'POST':
        if request.POST['password'] == request.POST['confirm_password']:
            pass
        else:
            ret['passwords_didnt_match'] = True

    return ret

