from annoying.decorators import render_to

import pdb
import logging
import datetime

#markup page when we don't specify a album_id (get it from request)
@render_to('faq.html')
def faq(request):
    return {}
