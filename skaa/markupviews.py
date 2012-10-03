# Create your views here.
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.core.urlresolvers import reverse
from django.utils import simplejson
from django.http import HttpResponse

from annoying.decorators import render_to
from annoying.functions import get_object_or_None

from common.models import Pic
from common.models import Batch
from common.models import Group
from common.models import Job
from common.models import ungroupedId
from common.decorators import passes_test
from models import Markup

import pdb
import logging

def belongs_on_this_markup_page(request, batch_id, sequence):
    batch_id = int(batch_id)
    b = get_object_or_None(Batch, id=batch_id)

    #this batch doesn't exist
    if b is None:
        return False

    #if the user isn't logged in
    if not request.user.is_authenticated():
        #get batch from session
        req_batch = Batch.get_unfinished(request).id
        #does it match the batch they are trying to view?
        if req_batch == batch_id:
            return True
        else:
            return False
    
    #the user is logged in by this point
    profile = request.user.get_profile()

    #is batch owner
    if profile == b.userprofile:
        return True

    j = get_object_or_None(Job, skaa_batch=batch_id)

    #is doctor of job
    if j.doctor == profile:
        return True

    #is a doctor and the job doesn't have a doctor (aka they can view it)
    if j.doctor is None and profile.is_doctor:
        return True

    #assume false
    return False

def markup_page_test(request, sequence):
    batch = Batch.get_unfinished(request)
    if batch:
        return True
    return False

#markup page when we don't specify a batch_id (get it from request)
@render_to()
@passes_test(markup_page_test, 'upload')
def markup_page(request, sequence):
    batch_id = Batch.get_unfinished(request).id
    return markup_page_batch(request, batch_id, sequence)

#markup page when we specify a batch_id
@render_to()
@passes_test(belongs_on_this_markup_page, 'upload')
def markup_page_batch(request, batch_id, sequence):
    sequence = int(sequence)
    batch = Batch.objects.get( pk=int(batch_id) )

    pics = Pic.objects.filter( batch=batch )

    if len(pics) == 0:
      # No pictures. How did they get here? Direct typing of the url?
      # Let's send them back to the upload page
        return redirect('upload')
    
    # We need valid sequences in this view. Set them. (This will fall through
    # if that's not necessary)
    batch.set_sequences()

    logging.info('sequence=%d, batch.id=%d, batch_num=%d' % (sequence, batch.id, batch.num_groups))

    logging.info('len(pics)=%d' % len(pics))
    group = Group.objects.get(sequence=sequence,batch=batch)

    doc_pic_groups = group.get_doctor_pics()
    doc_pics = []
    #although logic dictates that if we have doc_pics then we should have a job,
    #what does it hurt to check again?
    j = get_object_or_None(Job, skaa_batch=batch)
    if j is not None:
        for doc_pic_group in doc_pic_groups:
            #TODO add logic to figure out if we show watermark pic or other pic
            doc_pics.append(doc_pic_group.watermark_pic)


    read_only = group.is_locked

    pics = pics.filter( group__exact=group)
    
    job_page = 'job_page'

    if request.user.is_authenticated() and request.user.get_profile().is_doctor:
        job_page = 'doc_job_page'

    if sequence == batch.num_groups:
        if read_only:
            next_url = reverse(job_page)
        else:
            next_url = reverse('set_price')
    else:
        next_url = reverse('markup_batch', args=[batch.id, sequence+1])

    if sequence == 1:
        if read_only:
            previous_url= reverse(job_page)
        else:
            previous_url = reverse('upload')
    else:
        previous_url = reverse('markup_batch', args = [batch.id, sequence-1])

    template_name = 'markup_ro.html'if read_only else 'markup.html'

    return { 'pics' : pics, 'next_url' : next_url, 'previous_url' : previous_url, 
            'TEMPLATE': template_name , 'group_id': group.id, 'doc_pics':doc_pics}

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
        batch = Batch.get_unfinished(request)
        batch_id = batch.id if batch else None
        if batch_id and markup.pic.batch_id == batch_id:
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
def pic_instruction_handler(request):
    #pdb.set_trace()
    data = simplejson.loads(request.body)
    pic = Pic.objects.get(uuid=data['uuid'])
    if can_modify_pic(request, pic):
        pic.general_instructions = data['general_instructions']
        pic.save()
    
    return HttpResponse(simplejson.dumps({}), mimetype='application/json')
