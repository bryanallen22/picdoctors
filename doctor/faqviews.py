from annoying.decorators import render_to

import ipdb
import logging; log = logging.getLogger('pd')
import datetime

@render_to('doc_faq.html')
def doc_faq(request):
    return { }
