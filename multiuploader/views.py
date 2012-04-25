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

@render_to('upload.html')
def upload_page(request):
    logging.info('got to %s' % __name__)
    return locals()

# TODO - make this csrf_protect
@csrf_exempt
def upload_handler(request):
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
            pic.save()

            logging.info('File saving done')
            
            result = []
            result.append({"name"             : pic.title, 
                           "size"             : pic.get_size(),
                           "url"              : pic.get_url(),
                           "thumbnail_url"    : pic.get_thumb_url(),
                           # TODO - url lookup here
                           "delete_url"    : '/delete_pic/' + pic.uuid,
                           # TODO - change type to 'DELETE' ?
                           "delete_type"   : "POST",})

            response_data = simplejson.dumps(result)
            logging.info(response_data);
            return HttpResponse(response_data, mimetype='application/json')
        else:
            # file is None. How did we get here?
            return HttpResponse('[ ]', mimetype='application/json')

    else: #GET
        # TODO - get rid of this temporary debug code:
        response = '[ ]'
        #response = '[\
        #{"name": "DSC_1426",
        # "url": "http://picdoctors.s3.amazonaws.com/pics/70e50d48a9b0455e8276f5d2d7d27334.jpg",
        # "thumbnail_url": "http://picdoctors.s3.amazonaws.com/thumbs/70e50d48a9b0455e8276f5d2d7d27334.jpg",
        # "delete_type": "POST",
        # "delete_url": "/delete_pic/70e50d48a9b0455e8276f5d2d7d27334",
        # "size": 4437082} \
        #]'
        return HttpResponse(response, mimetype='application/json')
        #return HttpResponse('[ ]', mimetype='application/json')

