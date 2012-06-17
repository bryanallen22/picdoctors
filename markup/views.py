# Create your views here.
from django.shortcuts import render_to_response, get_object_or_404, redirect

from annoying.decorators import render_to

from upload.views import get_batch_id
from upload.models import Pic
from upload.models import Batch

import logging

@render_to('markup.html')
def markup_page(request):
    batch_id = get_batch_id(request)
    pics = Pic.objects.filter( batch__exact=batch_id );
    logging.info('batch_id is %d' % batch_id)
    logging.info('len(pics)=%d' % len(pics))
    if len(pics) == 0:
      # No pictures. How did they get here? Direct typing of the url?
      # Let's send them back to the upload page
      return redirect('upload')

    # Just working on design at the moment, so I'm just going to hard code
    # Viewing just the first pic
    return locals()


