from annoying.decorators import render_to

import ipdb
import logging; log = logging.getLogger('pd')
import datetime

@render_to('howitworks.html')
def howitworks(request):
    return {}
