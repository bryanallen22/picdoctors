from annoying.decorators import render_to

import ipdb

@render_to('home.html')
def home(request):
    return {}
