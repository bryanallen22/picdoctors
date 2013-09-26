from annoying.decorators import render_to
from skaa.progressbarviews import get_progressbar_vars
from skaa.markupviews import belongs_on_this_markup_page, markup_to_dict
from skaa.models import Markup
from django.http import HttpResponse

from django.utils import simplejson

from common.models import Job, Album, Group, Pic
from common.functions import json_result
from skaa.markupviews import can_modify_markup
from annoying.functions import get_object_or_None

import ipdb

@render_to('home.html')
def home(request):
    return {}

def users_endpoint(request, user_id):
    user = {
            'id': -1,
            'nickname': 'visitor',
            'email': 'email',
            'isLoggedIn': False
           }

    profile = request.user
  
    if profile.is_authenticated():
        user['id'] = profile.id
        user['nickname'] = profile.nickname
        user['email'] = profile.email
        user['isLoggedIn'] = True

    return json_result({"user":user})

def can_modify_markup(request, markup_id=None):
    pic = None
    if markup_id:
        markup = get_object_or_None(Markup, id=markup_id)
        if markup:
            pic = markup.pic
    else:
        data = simplejson.loads(request.body)
        try:
            pic = Pic.objects.get(id=data['markup']['pic'])
        except: 
            return False

    if not pic:
        return False

    # this gets the only album associated with your session
    album = Album.get_unfinished(request)

    #all pics are in a album, all pics are in a grouping
    if pic.group and pic.album and pic.album == album:
        return not pic.group.is_locked

    return False


def markups_endpoint(request, markup_id=None):
    # POST /markups_endpoint/ -- create a new markup
    result = {}
    if request.method == 'POST':
        if can_modify_markup(request):
            data = simplejson.loads(request.body)
            data = data['markup']
            pic = Pic.objects.get(id=data['pic'])

            markup = Markup()
            markup.pic = pic
            markup.left = data['left']
            markup.top = data['top']
            markup.width = data['width']
            markup.height = data['height']
            markup.save()

            m = markup_to_dict(markup)
            m["pic"] = pic.id
            return json_result({'markup': m})

    elif request.method == 'PUT':
        if can_modify_markup(request):
            data = simplejson.loads(request.body)
            data = data['markup']
            markup = Markup.objects.get(id=markup_id)

            markup.description = data['description']
            markup.save()

            result = {}

    elif request.method == 'DELETE':
        m = Markup.objects.get(id=markup_id)
        if can_modify_markup( request, markup_id):
            m.delete()
        result = {}

    response_data = simplejson.dumps(result)
    return HttpResponse(response_data, mimetype='application/json')

def can_modify_pic(request, pic):
   album = Album.get_unfinished(request)
   album_id = album.id if album else None
   return album_id and pic.album_id == album_id


def pics_endpoint(request, pic_id=None):
    # POST /pics_endpoint/ -- create a new markup
    if request.method == 'PUT':
        data = simplejson.loads(request.body)
        data = data['pic']
        pic = Pic.objects.get(id=pic_id)

        if can_modify_pic(request, pic):
            pic.description= data['description']
            pic.save()
            result = {}

    response_data = simplejson.dumps(result)
    return HttpResponse(response_data, mimetype='application/json')

def albums_endpoint(request, album_id):
    if not belongs_on_this_markup_page(request, album_id,-1):
        return HttpResponse('Unauthorized', status=401)
    
    album = get_object_or_None(Album, pk=album_id)
    #make sure the sequences are set here :)
    album.set_sequences()

    response = {}
    response["album"] = prepAlbum(album, request)
    response["groups"] = prepGroups(album, request)
    response["pics"] = prepPics(album)
    response["docPics"] = prepDocPics(album, request)
    response["markups"] = prepMarkups(response["pics"])
    return json_result(response)

def prepAlbum(album, request):
    groups = Group.get_album_groups(album)
    groupings = [g.id for g in groups]
    job = album.get_job_or_None()
    owner_id = -1
    doctor_id = -1

    if album.userprofile is not None:
        owner_id = album.userprofile.id

    if job is not None:
        if job.doctor is not None:
            doctor_id = job.doctor.id

    albumJson = {
            'id': album.id, 
            'groups': groupings,
            'finished': album.finished,
            'owner' : owner_id,
            'doctor' : doctor_id
            }

    return albumJson

def prepGroups(album, request):
    groupsJson = []

    groups = Group.get_album_groups(album)
    job = album.get_job_or_None()
    for group in groups:
        pics = Pic.get_group_pics(group)
        pic_ids = [p.id for p in pics]
        doc_pic_ids = []

        if job is not None:
            doc_pics = group.get_doctor_pics(job, request.user)
            doc_pic_ids = [dp.get_pic(request.user, job).id for dp in doc_pics]

        model = {
           'id': group.id, 
           'album': album.id, 
           'pics': pic_ids,
           'docPics': doc_pic_ids
                }
        groupsJson.append(model)

    return groupsJson

def prepDocPics(album, request):
    doc_pics = []
    job = album.get_job_or_None()
    if job is None:
        return []
    
    groups = Group.get_album_groups(album)
    # ipdb.set_trace()
    for group in groups:
        doc_pic_groups = group.get_doctor_pics(job, request.user)
        for doc_pic_group in doc_pic_groups:
            pic = doc_pic_group.get_pic(request.user, job)
            model = buildDocPic(group, pic)
            doc_pics.append(model)

    return doc_pics

def buildDocPic(group, pic):
    return {
        'id': pic.id,
        'group': group.id,
        'preview_url': pic.get_preview_url(),
        'original_url': pic.get_original_url(),
        'width': pic.preview_width,
        'height': pic.preview_height,
        'created': pic.created.isoformat(' ')
           }


def prepPics(album):
    pics_ret = []

    groups = Group.get_album_groups(album)
    for group in groups:
        pics = Pic.get_group_pics(group)
        for pic in pics:
            markups = Markup.objects.filter(pic__id=pic.id)
            markupIds = [m.id for m in markups]
            model = {
                 'id': pic.id,
                 'group': group.id,
                 'description': pic.description,
                 'preview_url': pic.get_preview_url(),
                 'original_url': pic.get_original_url(),
                 'width': pic.preview_width,
                 'height': pic.preview_height,
                 'markups': markupIds
                    }
       
            pics_ret.append(model)

    return pics_ret

def prepMarkups(pics):
    markups = []
    for pic in pics:
        p = get_object_or_None(Pic, id=pic["id"])
        # I wanna redo this
        markupList = p.get_markups()
        for m in markupList:
            m["pic"] = p.id

        markups.extend(markupList)
    return markups


