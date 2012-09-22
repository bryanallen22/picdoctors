# Create your views here.
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.core.urlresolvers import reverse
from django.views.decorators.csrf import csrf_protect
from django.utils import simplejson
from django.http import HttpResponse

from annoying.decorators import render_to

from skaa.uploadviews import get_batch_id
from common.models import Pic
from common.models import Batch
from common.models import Group
from common.models import ungroupedId
from models import Markup

import pdb
import logging

@render_to('set_price.html')
def set_price(request):
    if request.method == 'GET':
        pass
    elif request.method == 'POST':
        pass
    return { }


