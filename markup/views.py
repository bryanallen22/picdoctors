# Create your views here.
from django.shortcuts import render_to_response, get_object_or_404

from annoying.decorators import render_to

@render_to('markup.html')
def markup_page(request):
    return locals()

