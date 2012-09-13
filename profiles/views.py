from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.core.urlresolvers import reverse
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.http import HttpResponse

from annoying.decorators import render_to

from upload.views import get_batch_id
from upload.models import Batch

import pdb
import logging

@render_to('signin.html')
def signin(request):
    return { }

