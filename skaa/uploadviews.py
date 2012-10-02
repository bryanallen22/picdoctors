import logging

from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import redirect

#importing json parser to generate plugin friendly json response
from django.utils import simplejson

from django.template import RequestContext
from annoying.decorators import render_to
from annoying.functions import get_object_or_None

from django.core.files.uploadedfile import UploadedFile

from common.models import Pic
from common.models import Batch
from common.models import Group
from common.models import Job
from common.models import ungroupedId
from common.decorators import passes_test
import pdb

def pic_json(pic):
    return {"name"             : pic.title, 
            "size"             : 0, # pic.get_size(), // This is sloooow!
            "url"              : pic.get_preview_url(),
            "thumbnail_url"    : pic.get_thumb_url(),
            # TODO - url lookup here
            "delete_url"       : '/delete_pic/' + pic.uuid,
            # TODO - change type to 'DELETE' ?
            "delete_type"      : "POST",
            "uuid"             : pic.uuid }

@render_to('upload.html')
def upload_page(request):
    batch = Batch.get_unfinished(request)
    if not batch:
        batch = Batch.create_batch(request)
    logging.info('batch.id is %d' % batch.id)
    pics = Pic.objects.filter( batch__exact=batch.id );
    return { "pics" : pics, "ungroupedId" :  ungroupedId }

@render_to('need_cookies.html')
def need_cookies(request):
    logging.info('got to %s' % __name__)
    return locals()

def has_doc_upload_access(request):
    #invalid post
    if not request.POST.__contains__('group_id'):
        return False
    
    group_id = -1
    #convert group_id to int else, return false
    try:
        group_id = int(request.POST['group_id'])
    except:
        return False
    
    #not logged in
    if not request.user.is_authenticated():
        return False

    profile = request.user.get_profile()

    #not a doctor
    if not profile.is_doctor:
        return False

    
    group = get_object_or_None(Group, id=group_id)

    if group is None:
        return False

    job = get_object_or_None(Job, skaa_batch=group.batch.id)

    if job is None:
        return False

    if job.doctor == profile:
        return True

    return False
    

@csrf_protect
@passes_test(has_doc_upload_access, '/')
def doc_upload_handler(request):
    logging.info('got to %s' % __name__)
    if request.method == 'POST':
        if request.FILES == None:
            return HttpResponseBadRequest('Must have files attached!')
        #don't worry, we validate the group_id at the decorator
        group_id = int(request.POST['group_id'])
        group = get_object_or_None(Group, id=group_id )
        # Save this off into the database
        logging.info('got to %s' % __name__)
        file = request.FILES[u'doc_file']
        if file is not None:
            logging.info(file.name)
            pic = Pic(path_owner="doc")
            pic.set_file(file)
            pic.save()
            #create a new entry in the DocPicGroup
            group.add_doctor_pic(pic)

            logging.info('File saving done')
            
            result = []
            result.append(pic_json(pic))

            response_data = simplejson.dumps(result)
     
    #redirect to where they came from
    return redirect(request.META['HTTP_REFERER'])

#Since the browser is posting this it includes the CSRF token
@csrf_protect
def upload_handler(request):
    logging.info('got to %s' % __name__)
    if request.method == 'POST':
        if request.FILES == None:
            return HttpResponseBadRequest('Must have files attached!')
        
        #remove database groupings (this will force them to be regrouped in database)
        delete_groupings(request)

        # Save this off into the database
        logging.info('got to %s' % __name__)
        file = request.FILES[u'files[]']
        if file is not None:
            logging.info(file.name)
            pic = Pic()
            pic.set_file(file)
            batch = Batch.get_unfinished(request)
            pic.batch = batch if batch else Batch.create_batch(request)
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

        response_data = simplejson.dumps(result)
        #logging.info(response_data)
        return HttpResponse(response_data, mimetype='application/json')

@csrf_protect
def group_pic_handler(request):
    data = simplejson.loads(request.body)

    if request.method == 'POST':
        # Create a group
        group_id = data['group_id']
    else: # DELETE
        group_id = ungroupedId

    #Delete old groupings, remake when they hit markup
    delete_groupings(request)

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

@csrf_protect
def delete_pic_handler(request):
    if request.method == 'DELETE':
        data = simplejson.loads(request.body)
        pic  = Pic.objects.get(uuid__exact=data['uuid']);
        if pic:
            delete_groupings(request)
            pic.delete()
            return HttpResponse('{ "success" : true }', mimetype='application/json')
    return HttpResponse('{ "success" : false }', mimetype='application/json')

def delete_groupings(request):
    batch = Batch.get_unfinished(request)
    if batch:
        logging.info('deleting %d' % batch.id)
        Group.objects.filter(batch=batch.id).delete()

