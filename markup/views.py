# Create your views here.
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.core.urlresolvers import reverse

from annoying.decorators import render_to

from upload.views import get_batch_id
from upload.models import Pic
from upload.models import Batch
from upload.models import ungroupedId


import logging

def set_group_ids(request, batch_id):
    # Sets group_id for each picture in the batch. Note that this
    # will quite happily override any existing group_id that was
    # already set.
    pics = Pic.objects.filter( batch__exact=batch_id )

    # This doesn't feel like the most efficient way to get a sorted,
    # unique list, but it works
    browser_ids = sorted(list(set([pic.browser_group_id for pic in pics])))

    next_group_id = 1
    for id in browser_ids:
        # Find all pics that match this id
        matches = pics.filter( browser_group_id__exact=id )
        if id != ungroupedId:
            # All matching pics get next_group_id
            for pic in matches:
                pic.group_id = next_group_id
                pic.save()
            next_group_id += 1
        else:
            # All ungrouped pics get their own group_id
            for pic in matches:
                pic.group_id = next_group_id
                pic.save()
                next_group_id += 1

    batch = Batch.objects.get( pk=batch_id )
    batch.num_groups = (next_group_id - 1)
    batch.save()

@render_to('markup.html')
def markup_page(request, group_id):
    group_id = int(group_id)
    batch_id = get_batch_id(request)
    batch = Batch.objects.get( pk=batch_id )

    # On our first page, we set the group ids.
    # Note: If they hit this view multiple times, we'll keep resetting these.
    # Could that cause problems some day?
    if group_id == 1:
        set_group_ids(request, batch_id)

    logging.info('group_id=%d, batch_id=%d' % (group_id, batch_id))

    pics = Pic.objects.filter( batch__exact=batch_id )
    logging.info('len(pics)=%d' % len(pics))
    pics = pics.filter( group_id__exact=group_id )

    if len(pics) == 0:
      # No pictures. How did they get here? Direct typing of the url?
      # Let's send them back to the upload page
      return redirect('upload')

    if group_id == batch.num_groups:
        next_url = '/hoodles/'
    else:
        next_url = reverse('markup', args=[group_id+1])
    # Just working on design at the moment, so I'm just going to hard code
    # Viewing just the first pic
    return { 'pics' : pics, 'next_url' : next_url }

