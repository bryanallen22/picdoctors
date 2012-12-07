from annoying.decorators import render_to

import pdb
import logging
import datetime

@render_to('howitworks.html')
def howitworks(request):
    return {}
