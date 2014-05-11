from annoying.decorators import render_to

from doctor.withdrawviews import minimum_withdraw

import ipdb
import logging; log = logging.getLogger('pd')
import datetime

@render_to('doc_faq.html')
def doc_faq(request):
    return {
        'minimum_withdraw' : minimum_withdraw,
    }
