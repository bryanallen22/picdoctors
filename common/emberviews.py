from annoying.decorators import render_to
from skaa.progressbarviews import get_progressbar_vars
from skaa.markupviews import belongs_on_this_markup_page
from skaa.models import Markup
from django.http import HttpResponse

from common.models import Job, Album, Group, Pic
from common.functions import json_result
from skaa.markupviews import can_modify_markup
from annoying.functions import get_object_or_None

import ipdb

@render_to('home.html')
def home(request):
    ret = get_progressbar_vars(request, 'markup')
    return ret

def users_endpoint(request, user_id):
    user = {
            'id': -1,
            'nickname': 'visitor',
            'email': 'email'
           }

    profile = request.user
  
    if profile.is_authenticated():
        user['id'] = profile.id
        user['nickname'] = profile.nickname
        user['email'] = profile.email

    return json_result({"user":user})

def albums_endpoint(request, album_id):
    if not belongs_on_this_markup_page(request, album_id,-1):
        return HttpResponse('Unauthorized', status=401)
    
    album = get_object_or_None(Album, pk=album_id)

    response = {}
    response["album"] = prepAlbum(album)
    response["groups"] = prepGroups(album)
    response["pics"] = prepPics(album)
    response["markups"] = prepMarkups(response["pics"])
    return json_result(response)

def markups_endpoint(request, markup_id=None):
    # POST /markups_handler/ -- create a new markup
    if request.method == 'POST':
        return json_result({'markup': {'id':87686}})
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

    return json_result({id:87686})

def prepAlbum(album):
    groups = Group.get_album_groups(album)
    groupings = [g.id for g in groups]

    albumJson = {'id': album.id, 'groups': groupings}

    return albumJson

def prepGroups(album):
    groupsJson = []

    groups = Group.get_album_groups(album)
    for group in groups:
        pics = Pic.get_group_pics(group)
        picIds = [p.uuid for p in pics]
        model = {
           'id': group.id, 
           'album': album.id, 
           'pics': picIds
                }
        groupsJson.append(model)

    return groupsJson

def prepPics(album):
    picsJson = []

    groups = Group.get_album_groups(album)
    for group in groups:
        pics = Pic.get_group_pics(group)
        for pic in pics:
            markups = Markup.objects.filter(pic__uuid__exact=pic.uuid)
            markupIds = [m.id for m in markups]
            model = {
                 'id': pic.uuid,
                 'group': group.id,
                 'general_instructions': pic.general_instructions,
                 'preview_url': pic.get_preview_url(),
                 'width': pic.preview_width,
                 'height': pic.preview_height,
                 'markups': markupIds
                    }
       
            picsJson.append(model)

    return picsJson 

def prepMarkups(pics):
    markups = []
    for pic in pics:
        p = get_object_or_None(Pic, uuid=pic["id"])
        markupList = p.get_markups()
        for m in markupList:
            m["pic"] = m["pic_uuid"]
            del m["pic_uuid"]

        markups.extend(markupList)
    return markups

