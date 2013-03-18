# Create your views here.
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.core.urlresolvers import reverse
from django.utils import simplejson
from django.http import HttpResponse

from annoying.decorators import render_to
from annoying.functions import get_object_or_None

from common.models import Pic
from common.models import Album
from common.models import Group
from common.models import Job
from common.models import ungroupedId
from common.decorators import passes_test
from common.functions import get_profile_or_None
from common.functions import get_unfinished_album
from models import Markup

import ipdb
import logging

def belongs_on_this_markup_page(request, album_id, sequence):
    album_id = int(album_id)
    album = get_object_or_None(Album, id=album_id)

    #this album doesn't exist
    if album is None:
        return False

    #if the user isn't logged in
    if not request.user.is_authenticated():
        #get album from session
        req_album = Album.get_unfinished(request)
        #does it match the album they are trying to view?
        if req_album and req_album.id == album_id:
            return True
        else:
            return False
    
    #the user is logged in by this point
    profile = request.user

    #is album owner
    if profile == album.userprofile:
        return True

    j = get_object_or_None(Job, album=album_id)

    if not j:
        return False

    # the job doesn't have a doctor and the profile is a doctor (aka they can view it)
    if not j.doctor and profile.isa('doctor'):
        return True

    # is doctor of job and the job isn't finished!
    if j.doctor and j.doctor == profile and j.status != Job.USER_ACCEPTED :
        return True

    #assume false
    return False

def markup_page_test(request, sequence):
    album = Album.get_unfinished(request)
    if album:
        return True
    return False

#markup page when we don't specify a album_id (get it from request)
@render_to('markup.html')
@passes_test(markup_page_test, 'upload')
def markup_page(request, sequence):
    album, redirect_url = get_unfinished_album(request)
    if not album:
        # Either send them to upload or merge
        return redirect(redirect_url)
    return markup_page_album(request, album.id, sequence)

#markup page when we specify a album_id
@render_to('markup.html')
@passes_test(belongs_on_this_markup_page, 'upload')
def markup_page_album(request, album_id, sequence):
    sequence = int(sequence)
    album = Album.objects.get( pk=int(album_id) )
    job = album.get_job_or_None()
    profile = get_profile_or_None(request)

    pics = Pic.objects.filter( album=album )

    if len(pics) == 0:
      # No pictures. How did they get here? Direct typing of the url?
      # Let's send them back to the upload page
        return redirect('upload')
    
    # We need valid sequences in this view. Set them. (This will fall through
    # if that's not necessary)
    album.set_sequences()

    logging.info('sequence=%d, album.id=%d, album_num=%d' % (sequence, album.id, album.num_groups))

    logging.info('len(pics)=%d' % len(pics))
    group = Group.objects.get(sequence=sequence,album=album)
    doc_pic_groups = group.get_doctor_pics(job, profile)
    doc_pics = []
    revision = len(doc_pic_groups) + 1
    for doc_pic_group in doc_pic_groups:
        revision -= 1
        doc_pics.append((revision, doc_pic_group.get_pic(profile, job)))


    read_only = group.is_locked

    pics = pics.filter(group__exact=group)
    
    job_page = 'job_page'
    is_job_doctor = False

    if profile and profile.isa('doctor'):
        job_page = 'new_job_page'
        if job and job.doctor == profile:
            is_job_doctor = True
            job_page = 'doc_job_page'

    is_job_user = False
    # AKA I am the user
    if (profile and profile.isa('skaa')) or not job:
        is_job_user = True

    #previous next links
    if sequence == album.num_groups:
        if read_only:
            next_url = reverse(job_page)
        else:
            next_url = reverse('set_price')
    else:
        next_url = reverse('markup_album', args=[album.id, sequence+1])

    if sequence == 1:
        if read_only:
            previous_url= reverse(job_page)
        else:
            previous_url = reverse('upload')
    else:
        previous_url = reverse('markup_album', args = [album.id, sequence-1])

    return { 
            'pics'          : pics, 
            'next_url'      : next_url, 
            'previous_url'  : previous_url, 
            'group_id'      : group.id, 
            'doc_pics'      : doc_pics, 
            'is_job_doctor' : is_job_doctor, 
            'is_job_user'   : is_job_user, 
            'read_only'     : read_only,
    }

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

    #ipdb.set_trace()
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
def can_modify_markup(request, markup_id=None):
    pic = None
    if markup_id:
        markup = get_object_or_None(Markup, id=markup_id)
        if markup:
            pic = markup.pic
    else:
        data = simplejson.loads(request.body)
        pic = Pic.objects.get(uuid__exact=data['pic_uuid'])
    
    if not pic:
        return False

    album = Album.get_unfinished(request)

    #all pics are in a album, all pics are in a grouping
    if pic.group and pic.album and pic.album == album:
        return not pic.group.is_locked

    return False

def markups_handler(request, markup_id=None):
    # POST /markups_handler/ -- create a new markup
    if request.method == 'POST':
        if can_modify_markup(request):
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
        if can_modify_markup(request):
            data = simplejson.loads(request.body)
            markup = Markup.objects.get(id=data['id'])

            album = Album.get_unfinished(request)
            album_id = album.id if album else None
            if album_id and markup.pic.album_id == album_id:
                apply_markup_whitelist(markup, data)
                markup.save()
        
        # Return any modified properties... Uh.... I don't forsee
        # overriding any of the things that they set...
        result = {}
    elif request.method == 'DELETE':
        m = Markup.objects.get(id=markup_id)
        if can_modify_markup( request, markup_id):
            m.delete()
        result = {}

    response_data = simplejson.dumps(result)
    return HttpResponse(response_data, mimetype='application/json')

#Implement logic to validate user has relation to album/pic
def can_modify_pic(request, pic):
    if pic:
        if pic.album:
            req_album = Album.get_unfinished(request)
            if req_album and req_album.id == pic.album.id:
                return True
    return False

# TODO return error when it doesn't save
def pic_instruction_handler(request):
    #ipdb.set_trace()
    data = simplejson.loads(request.body)
    pic = Pic.objects.get(uuid=data['uuid'])
    if can_modify_pic(request, pic):
        pic.general_instructions = data['general_instructions']
        pic.save()
    
    return HttpResponse(simplejson.dumps({}), mimetype='application/json')
