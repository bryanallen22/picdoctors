from annoying.decorators import render_to

import pdb
import logging
import datetime

@render_to('faq.html')
def faq(request):
    return {}
