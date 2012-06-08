import logging

from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.shortcuts import render_to_response, get_object_or_404
from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest

#importing json parser to generate plugin friendly json response
from django.utils import simplejson

from django.template import RequestContext
from annoying.decorators import render_to
from django.core.files.uploadedfile import UploadedFile

from models import Pic
from models import Batch
from models import Markup
from models import Group
from models import UserProfile

def create_batch(request):
    # If there isn't already a batch assigned, assign it now
    if 'batch_id' not in request.session:
        batch = Batch()
        batch.save()
        request.session['batch_id'] = batch.id
    return request.session['batch_id']

def get_batch(request):
    # This will create a batch if necessary
    batch = Batch.objects.get(pk=create_batch(request))
    return batch

def pic_json(pic):
    return {"name"             : pic.title, 
            "size"             : pic.get_size(),
            "url"              : pic.get_url(),
            "thumbnail_url"    : pic.get_thumb_url(),
            # TODO - url lookup here
            "delete_url"    : '/delete_pic/' + pic.uuid,
            # TODO - change type to 'DELETE' ?
            "delete_type"   : "POST",}

@render_to('upload.html')
def upload_page(request):
    logging.info('got to %s, batch_id is %d' % (__name__, create_batch(request)))
    return locals()

@render_to('needcookies.html')
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
        pics = Pic.objects.filter(batch__exact=create_batch(request))

        for pic in pics:
            result.append(pic_json(pic))

        response_data = simplejson.dumps(result)
        #logging.info(response_data)
        return HttpResponse(response_data, mimetype='application/json')

