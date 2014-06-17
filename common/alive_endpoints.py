from django.http import HttpResponse
from django.utils import simplejson
from common.functions import json_result
import ipdb

def skaa_live_on(request):
    response = {
            'indeed':'they do'
            }
    return json_result(response)
