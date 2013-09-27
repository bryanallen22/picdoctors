import logging; log = logging.getLogger('pd')

from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import redirect

#importing json parser to generate plugin friendly json response
from django.utils import simplejson

from django.template import RequestContext
from annoying.decorators import render_to, ajax_request
from annoying.functions import get_object_or_None

from django.core.files.uploadedfile import UploadedFile

from common.functions import get_unfinished_album, get_profile_or_None
from common.functions import json_result
from common.models import Pic
from common.models import Album
from common.models import Group
from common.models import Job
from common.models import ungroupedId
from common.decorators import passes_test
from skaa.progressbarviews import get_progressbar_vars

from PIL import Image
from StringIO import StringIO
from django.core.files.uploadedfile import InMemoryUploadedFile

from django.core.urlresolvers import reverse
from tasks.tasks import saveWatermark

def pic_json(pic):
    return {"name"             : pic.title,
            "size"             : 0, # pic.get_size(), // This is sloooow!
            "url"              : pic.get_preview_url(),
            "thumbnail_url"    : pic.get_thumb_url(),
            "delete_url"       : reverse('delete_pic_handler') + pic.uuid,
            "delete_type"      : "DELETE",
            "uuid"             : pic.uuid }

@render_to('upload.html')
def upload_page(request):
    album, redirect_url = get_unfinished_album(request)
    if not album:
        if redirect_url == reverse('upload'):
            # Don't redirect them, they are already here!
            # Just make a album, already!
            album = Album.create_album(request)
        else:
            return redirect( redirect_url )

    log.info('album.id is %d' % album.id)
    pics = Pic.objects.filter( album__exact=album.id );

    ret = get_progressbar_vars(request, 'upload')
    ret.update( { "pics" : pics, "ungroupedId" :  ungroupedId } )
    # we do weird stuff, we don't know groups until later
    ret.update( { "markup_url" : "/home/#/albums/" + str(album.id) + "/markupEdit"})
    return ret

@render_to('need_cookies.html')
def need_cookies(request):
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

    profile = request.user

    #not a doctor
    if not profile.isa('doctor'):
        return False


    group = get_object_or_None(Group, id=group_id)

    if group is None:
        return False

    job = get_object_or_None(Job, album=group.album.id)

    if job is None:
        return False

    if job.doctor == profile:
        return True

    return False


@passes_test(has_doc_upload_access, '/')
@ajax_request
def doc_upload_handler(request):
    if request.method == 'POST':
        profile = get_profile_or_None(request)
        if request.FILES == None:
            return HttpResponseBadRequest('Must have files attached!')
        #don't worry, we validate the group_id at the decorator
        group_id = int(request.POST['group_id'])
        group = get_object_or_None(Group, id=group_id )
        
        # Save this off into the database
        file = request.FILES[u'doc_file']
        if file is not None:
            pickleable_pic = StringIO(file.read())
            # if you want to use the workers use the line below, watch out
            # I'm gonna make this non-asyncable
            # saveWatermark.apply_async(args=[profile.id, group_id, pickleable_pic])
            dp = saveWatermark(profile.id, group_id, pickleable_pic)
            
            job = get_object_or_None(Job, album=group.album.id)

            pic = dp.get_pic(request.user, job)
            log.info('File saving done')
            return pic.get_view_model(False)

    #redirect to where they came from
    return redirect(request.META['HTTP_REFERER'])

#Since the browser is posting this it includes the CSRF token
def upload_handler(request):
    if request.method == 'POST':
        if request.FILES == None:
            return HttpResponseBadRequest('Must have files attached!')

        #remove database groupings (this will force them to be regrouped in database)
        delete_groupings(request)

        # Save this off into the database
        file = request.FILES[u'files[]']
        if file is not None:
            log.info(file.name)
            pic = Pic()
            pic.set_file(file)
            album = Album.get_unfinished(request)
            pic.album = album if album else Album.create_album(request)
            pic.save()

            prof = request.user
            # If they aren't a skaa already, they are now...
            if prof.is_authenticated() and prof.isa('skaa') == False:
                prof.add_permission('skaa')

            log.info('File saving done')

            result = []
            result.append(pic_json(pic))

            album = Album.get_unfinished(request)
            album.kick_groups_modified()

            response_data = simplejson.dumps(result)
            #log.info(response_data)
            return HttpResponse(response_data, mimetype='application/json')
        else:
            log.error("file is None. How did we get here?")
            return HttpResponse('[ ]', mimetype='application/json')

    else: #GET
        result = []
        response_data = simplejson.dumps(result)
        return HttpResponse(response_data, mimetype='application/json')

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
        album = Album.get_unfinished(request)
        album.kick_groups_modified()
        return HttpResponse('{ "success" : true }', mimetype='application/json')
    else:
        return HttpResponse('{ "success" : false }', mimetype='application/json')

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
    album = Album.get_unfinished(request)
    if album:
        log.info('deleting all groupings in album id=%d' % album.id)
        Group.objects.filter(album=album.id).delete()
        album.kick_groups_modified()

    
