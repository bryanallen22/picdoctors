from annoying.decorators import render_to
from skaa.progressbarviews import get_progressbar_vars
from skaa.markupviews import belongs_on_this_markup_page
from django.http import HttpResponse

from common.models import Job, Album, Group, Pic
from common.functions import json_result
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
            model = {
                 'id': pic.uuid,
                 'group': group.id,
                 'general_instructions': pic.general_instructions,
                 'preview_url': pic.get_preview_url(),
                 'width': pic.preview_width,
                 'height': pic.preview_height
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

