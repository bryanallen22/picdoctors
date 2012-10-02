import logging

from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest

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

def get_batch_id(request):
    """
    Get the batch id from the session. If there isn't already a batch assigned, assign it now
    """
    batch = None
    if 'batch_id' not in request.session:
        if request.user.is_authenticated():
            batch = find_existing_batch(request.user.get_profile())
        
        if batch == None:
            batch = Batch()

        if request.user.is_authenticated():
            batch.userprofile = request.user.get_profile()
        batch.save()
        set_batch_id(request, batch.id)

    return request.session['batch_id']

def find_existing_batch(user_profile):
    #No profile means no batch
    if user_profile is None:
        return None
    batch = None

    #No latest batch associated with user means no batch
    try:
        batch = Batch.objects.filter(userprofile=user_profile).latest('created')
    except Exception as e:
        return None

    #No associated job means they never finished, return it!
    associated_job = get_object_or_None(Job, skaa_batch=batch)
    if associated_job is None:
        return batch
    else:
        return None

def set_batch_id(request, batch_id):
    if batch_id is None and 'batch_id' in request.session:
        del request.session['batch_id']
    
    if batch_id is not None:
        request.session['batch_id'] = batch_id

def get_batch(request):
    # This will create a batch if necessary
    batch = Batch.objects.get(pk=get_batch_id(request))
    return batch

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
    batch_id = get_batch_id(request)
    logging.info('batch_id is %d' % batch_id)
    pics = Pic.objects.filter( batch__exact=batch_id );
    return { "pics" : pics, "ungroupedId" :  ungroupedId }

@render_to('need_cookies.html')
def need_cookies(request):
    logging.info('got to %s' % __name__)
    return locals()

def has_doc_upload_access(request):
    pdb.set_trace()
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
        pdb.set_trace()
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
            pic.batch = get_batch(request)
            pic.save()

            logging.info('File saving done')
            
            result = []
            result.append(pic_json(pic))

            response_data = simplejson.dumps(result)
            return HttpResponse(response_data, mimetype='application/json')
        else:
            logging.error("file is None. How did we get here?")
            return HttpResponse('[ ]', mimetype='application/json')
    return HttpResponse('[ ]', mimetype='application/json')

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
    batch_id = get_batch_id(request) 
    logging.info('deleting %d' % batch_id)
    Group.objects.filter(batch=batch_id).delete()

