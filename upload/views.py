import logging

from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest

#importing json parser to generate plugin friendly json response
from django.utils import simplejson

from django.template import RequestContext
from annoying.decorators import render_to
from django.core.files.uploadedfile import UploadedFile

from models import Pic
from models import Batch
from models import ungroupedId

def get_batch_id(request):
    # If there isn't already a batch assigned, assign it now
    if 'batch_id' not in request.session:
        batch = Batch()
        batch.save()
        request.session['batch_id'] = batch.id
    return request.session['batch_id']

def get_batch(request):
    # This will create a batch if necessary
    batch = Batch.objects.get(pk=get_batch_id(request))
    return batch

def pic_json(pic):
    return {"name"             : pic.title, 
            "size"             : pic.get_size(),
            "url"              : pic.get_preview_url(),
            "thumbnail_url"    : pic.get_thumb_url(),
            # TODO - url lookup here
            "delete_url"       : '/delete_pic/' + pic.uuid,
            # TODO - change type to 'DELETE' ?
            "delete_type"      : "POST",
            "uuid"             : pic.uuid }

@render_to('upload.html')
def upload_page(request):
    batch_id = get_batch_id(request)
    logging.info('batch_id is %d' % batch_id)
    pics = Pic.objects.filter( batch__exact=batch_id );
    return { "pics" : pics, "ungroupedId" :  ungroupedId }

@render_to('need_cookies.html')
def need_cookies(request):
    logging.info('got to %s' % __name__)
    return locals()

# TODO - make this csrf_protect
@csrf_exempt
def upload_handler(request):
    logging.info('got to %s' % __name__)
    if request.method == 'POST':
        if request.FILES == None:
            return HttpResponseBadRequest('Must have files attached!')

        # Save this off into the database
        logging.info('got to %s' % __name__)
        file = request.FILES[u'files[]']
        if file is not None:
            logging.info(file.name)
            pic = Pic()
            pic.set_file(file)
            pic.batch = get_batch(request)
            pic.save()

            logging.info('File saving done')
            
            result = []
            result.append(pic_json(pic))

            response_data = simplejson.dumps(result)
            #logging.info(response_data)
            return HttpResponse(response_data, mimetype='application/json')
        else:
            logging.error("file is None. How did we get here?")
            return HttpResponse('[ ]', mimetype='application/json')

    else: #GET
        logging.info('got to %s' % __name__)
        # TODO - get rid of this temporary debug code:
        result = []
        # This ajax thing is slow. We preopulate it with the view/template
        # layers for the actual page
        #pics = Pic.objects.filter(batch__exact=get_batch_id(request))

        #for pic in pics:
        #    result.append(pic_json(pic))

        response_data = simplejson.dumps(result)
        #logging.info(response_data)
        return HttpResponse(response_data, mimetype='application/json')

# TODO - make this csrf_protect
@csrf_exempt
def group_handler(request):
    data = simplejson.loads(request.body)

    if request.method == 'POST':
        # Create a group
        group_id = data['group_id']
    else: # DELETE
        group_id = ungroupedId

    # Update the pictures
    pics = Pic.objects.filter(uuid__in=data['uuids']);
    ### We could update all of these at once with pics.update(), which
    ### would be more efficient, but I'm not going to for two reasons:
    ###   1) Doesn't call save() method or send pre_save or post_save signals.
    ###      Not a big deal today, but those look useful for later
    ###   2) I just don't expect grouping a small handful of pictures to
    ###      end up being a database hog.
    for pic in pics:
        pic.browser_group_id = group_id
        pic.save()

    if pics is not None:
        return HttpResponse('{ "success" : true }', mimetype='application/json')
    else:
        return HttpResponse('{ "success" : false }', mimetype='application/json')

# TODO - make this csrf_protect
@csrf_exempt
def delete_handler(request):
    if request.method == 'DELETE':
        data = simplejson.loads(request.body)
        pic  = Pic.objects.filter(uuid__exact=data['uuid']);
        if pic:
            pic.delete()
            return HttpResponse('{ "success" : true }', mimetype='application/json')
    return HttpResponse('{ "success" : false }', mimetype='application/json')

# TODO - make this csrf_protect
@csrf_exempt
def finish_batch(request):
    # Sets markup_group_id for each picture in the batch. Note that this
    # will quite happily override any existing markup_group_id that was
    # already set.
    if request.method == 'POST':
        batch_id = get_batch_id(request)
        pics = Pic.objects.filter( batch__exact=batch_id );

        # This doesn't feel like the most efficient way to get a sorted,
        # unique list, but it works
        browser_ids = sorted(list(set([pic.browser_group_id for pic in pics])))

        next_markup_group_id = 1
        for id in browser_ids:
            # Find all pics that match this id
            matches = pics.filter( browser_group_id__exact=id )
            if id is not ungroupedId:
                # All matching pics get next_markup_group_id
                for pic in matches:
                    pic.markup_group_id = next_markup_group_id
                    pic.save()
                next_markup_group_id += 1
            else:
                # All ungrouped pics get their own markup_group_id
                for pic in matches:
                    pic.markup_group_id = next_markup_group_id
                    pic.save()
                    next_markup_group_id += 1

        return HttpResponse('{ "success" : true }', mimetype='application/json')
    else:
        return HttpResponse('{ "success" : false }', mimetype='application/json')
