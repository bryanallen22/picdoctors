# Create your views here.
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.core.urlresolvers import reverse
from django.views.decorators.csrf import csrf_protect
from django.utils import simplejson
from django.http import HttpResponse

from annoying.decorators import render_to

from skaa.uploadviews import get_batch_id
from common.models import Pic
from common.models import Batch
from common.models import Group
from common.models import ungroupedId
from models import Markup

import pdb
import logging

@csrf_protect
def set_sequences(request, batch_id):
    # Sets sequence for each picture in the batch. Note that this
    # will quite happily override any existing sequence that was
    # already set.
    pics = Pic.objects.filter( batch__exact=batch_id )
    logging.info('setting sequences for batch_id %d' % batch_id)

    # This doesn't feel like the most efficient way to get a sorted,
    # unique list, but it works
    browser_ids = sorted(list(set([pic.browser_group_id for pic in pics])))
    logging.info(browser_ids)
    batch_instance = Batch.objects.get(pk=batch_id)
    next_sequence = 1
    for id in browser_ids:
        # Find all pics that match this id
        matches = pics.filter( browser_group_id__exact=id )
        if id != ungroupedId:
            # All matching pics get next_sequence
            logging.info('creating new group')
            g = Group(batch=batch_instance, sequence=next_sequence) 
            g.save()
            for pic in matches:
#                pic.group_id = next_sequence
                pic.group = g
                pic.save()
            next_sequence += 1
        else:
            # All ungrouped pics get their own sequence
            for pic in matches:
                logging.info('creating new group')
                g = Group(batch=batch_instance, sequence=next_sequence) 
                g.save()
 #               pic.group_id = next_sequence
                pic.group = g
                pic.save()
                next_sequence += 1

    batch = Batch.objects.get( pk=batch_id )
    next_sequence -= 1
    logging.info('Saving number of groups %d' % next_sequence)
    batch.num_groups = next_sequence
    batch.save()

@render_to('markup.html')
def markup_page(request, sequence):
    sequence = int(sequence)
    batch_id = get_batch_id(request)

    pics = Pic.objects.filter( batch__exact=batch_id )
    
    if len(pics) == 0:
      # No pictures. How did they get here? Direct typing of the url?
      # Let's send them back to the upload page
      return redirect('upload')
    
    #Reset the group Ids on 3 conditions, retgrouping, deleting of pics
    #or adding of new pics
    group_count = len(Group.objects.filter(batch=batch_id))
    logging.info('group count = %d' % group_count)
    if group_count == 0:
        set_sequences(request, batch_id)

    batch = Batch.objects.get( pk=batch_id )

    logging.info('sequence=%d, batch_id=%d, batch_num=%d' % (sequence, batch_id, batch.num_groups))

    logging.info('len(pics)=%d' % len(pics))
    group = Group.objects.get(sequence=sequence,batch=batch_id)
    pics = pics.filter( group__exact=group)

    if sequence == batch.num_groups:
        next_url = reverse('skaa_signin')
    else:
        next_url = reverse('markup', args=[sequence+1])

    if sequence == 1:
        previous_url = reverse('upload')
    else:
        previous_url = reverse('markup', args = [sequence-1])

    #TODO remove this tester code
    fake_button_text = 'Cheat and Delete Job' if group.is_locked else 'Cheat and Create Job' 
    return { 'pics' : pics, 'next_url' : next_url, 'previous_url' : previous_url, 'fake_button_text' : fake_button_text, 'is_locked' : group.is_locked }

def get_markup_whitelist():
    """ Returns whitelisted Markup attributes

    All names should be common to both the django Model and the
    backbone.js model"""

    return [
        'left',
        'top',
        'left',
        'top',
        'width',
        'height',
        'color',
        'color_name',
        'border_style',
        'description' ]



def apply_markup_whitelist(markup, data):
    # White list these. Don't iterate across keys or anything dumb
    for attr in get_markup_whitelist():
        setattr(markup, attr, data[attr])

    #pdb.set_trace()
    pic = Pic.objects.get(uuid__exact=data['pic_uuid'])
    markup.pic = pic

    return markup

def markup_to_dict(markup):
    """ Turn a Markup into a dict that will be easily translated to json later"""

    # Similar to apply_markup_whitelist above... don't want to
    # return everything in the table, lest there be a security hole.
    # Just return stuff that is whitelisted

    whitelist = get_markup_whitelist()
    # Manually append 'id' when doing reads, like right here
    whitelist.append('id')

    d = { k : getattr(markup, k) for k in whitelist }
    d['pic_uuid'] = markup.pic.uuid
    return d

# TODO: Should ALL markup_handler things go through here? Probably...
def can_modify_markup(markup, request):
    return True

@csrf_protect
def markups_handler(request, markup_id=None):
    # POST /markups_handler/ -- create a new markup
    if request.method == 'POST':
        data = simplejson.loads(request.body)

        markup = Markup()
        apply_markup_whitelist(markup, data)
        markup.save()

        result = { 'id' : markup.id }
        response_data = simplejson.dumps(result)
        return HttpResponse(response_data, mimetype='application/json')

    # GET /markups_handler/1234/
    elif request.method == 'GET' and markup_id is not None:
        result = {}

    # GET /markups_handler/?uuid='blah'
    elif request.method == 'GET' and markup_id is None:
        uuid = request.GET.get('uuid', None)
        if uuid is not None:
            markups = Markup.objects.filter(pic__uuid__exact=uuid)
            result = [ markup_to_dict(m) for m in markups ]
        else:
            result = {}

    elif request.method == 'PUT':
        data = simplejson.loads(request.body)
        markup = Markup.objects.get(id=data['id'])
        # So, derp wants to update that markup. But we don't want to blindly
        # assume they really own it, do we? That would let them update any
        # markup that they wanted. Do they really own this one?
        # TODO -- verify that this doesn't have some gaping security hole...
        # It probably does... See can_modify_markup() above
        batch_id = get_batch_id(request)
        if markup.pic.batch_id == batch_id:
            apply_markup_whitelist(markup, data)
            markup.save()
        
        # Return any modified properties... Uh.... I don't forsee
        # overriding any of the things that they set...
        result = {}
    elif request.method == 'DELETE':
        m = Markup.objects.get(id=markup_id)
        if can_modify_markup( request, m ):
            m.delete()
        result = {}

    response_data = simplejson.dumps(result)
    return HttpResponse(response_data, mimetype='application/json')

#Implement logic to validate user has relation to batch/pic
def can_modify_pic(request, pic):
    return True

# TODO return error when it doesn't save
@csrf_protect
def pic_instruction_handler(request):
    #pdb.set_trace()
    data = simplejson.loads(request.body)
    pic = Pic.objects.get(uuid=data['uuid'])
    if can_modify_pic(request, pic):
        pic.general_instructions = data['general_instructions']
        pic.save()
    
    return HttpResponse(simplejson.dumps({}), mimetype='application/json')
