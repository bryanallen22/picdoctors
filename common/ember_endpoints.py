from annoying.decorators import render_to
from skaa.progressbarviews import get_progressbar_vars
from skaa.markupviews import belongs_on_this_markup_page, markup_to_dict
from skaa.models import Markup
from django.http import HttpResponse

from django.utils import simplejson

from common.models import Job, Album, Group, Pic, DocPicGroup
from common.functions import json_result
from skaa.markupviews import can_modify_markup
from annoying.functions import get_object_or_None

from messaging.models import GroupMessage
from messaging.messageviews import build_messages, generate_message
from common.decorators import require_login_as

import ipdb

@render_to('home.html')
def home(request):
    return {}

def users_endpoint(request, user_id):
    profile = request.user

    if not profile.is_authenticated():
        return unauthenticated_user()

    user = {}
    user['id'] = profile.id
    user['nickname'] = profile.nickname
    user['email'] = profile.email
    user['isLoggedIn'] = True
    user['emailConfig'] = profile.id # He uses the profile id as a key to get the notifications to ignore

    roles = get_roles(profile)

    return json_result({
        "user":user,
        "roles": roles
        })

def unauthenticated_user():
    user = {
            'id': -1,
            'nickname': 'visitor',
            'email': 'email',
            'isLoggedIn': False,
            'roles': [-1]
           }

    return json_result({
        "user":user,
        "roles": [
            {
                "id" : -1,
                "name": "isDoctor"
            }
            ]
        })

def get_roles(profile):
    ret = []
    permissions = profile.user_permissions.all()
    for perm in permissions:
        p = {
                'id': perm.id,
                'name': perm.codename
            }
        ret.append(p)
    return ret

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
    # POST /pics_endpoint/ -- add pic description
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

    # So we you might be wondering why this is going down like this
    # well, it's easier to just match the format ember data expects
    response = {}
    response["album"] = prepAlbum(album, request)
    response["jobs"] = prepJobs(album)
    response["groups"] = prepGroups(album, request)
    pics = prepPics(album)
    response["docPicGroups"] = dpg = prepDocPicGroups(album, request)
    response["pics"] = pics + prepDocPics(dpg, request)
    response["markups"] = prepMarkups(response["pics"])
    response["messages"] = prepMessages(response["groups"], album, request)
    return json_result(response)

def prepAlbum(album, request):
    groups = Group.get_album_groups(album)
    groupings = [g.id for g in groups]
    job = album.get_job_or_None()
    owner_id = None
    doctor_id = None
    job_id = None

    if album.userprofile is not None:
        owner_id = album.userprofile.id

    if job is not None:
        job_id = job.id
        if job.doctor is not None:
            doctor_id = job.doctor.id

    albumJson = {
            'id': album.id,
            'groups': groupings,
            'finished': album.finished,
            'owner' : owner_id,
            'doctor' : doctor_id,
            'job': job_id
            }

    return albumJson

def prepJobs(album):
    job = album.get_job_or_None()
    job_json = []
    if job is not None:
        job_json.append({'id': job.id, 'status': job.status })
    return job_json

def prepGroups(album, request):
    groupsJson = []

    groups = Group.get_album_groups(album)
    job = album.get_job_or_None()
    for group in groups:
        pics = Pic.get_group_pics(group)
        pic_ids = [p.id for p in pics]
        doc_pic_ids = []
        doc_pic_group_ids = None

        if job is not None:
            doc_pic_groups = group.get_doctor_pics(job, request.user)
            doc_pic_group_ids = [dp.id for dp in doc_pic_groups]

        model = {
           'id': group.id,
           'album': album.id,
           'pics': pic_ids,
           'docPicGroups': doc_pic_group_ids
                }
        groupsJson.append(model)

    return groupsJson

def prepDocPics(doc_pic_groups, request):
    pics = []

    for dpg in doc_pic_groups:
        pics = pics + get_pic_view_models(dpg)

    return pics

def get_pic_view_models(doc_pic_view_model):
    pics = []

    dpg_record = get_object_or_None(DocPicGroup, id=doc_pic_view_model["id"])

    if doc_pic_view_model['pic'] is not None:
        pics.append(dpg_record.pic.get_view_model(False))

    if doc_pic_view_model['watermark_pic'] is not None:
        pics.append(dpg_record.watermark_pic.get_view_model(False))

    return pics


def prepDocPicGroups(album, request):
    doc_pic_groups_ret = []
    job = album.get_job_or_None()
    if job is None:
        return []

    groups = Group.get_album_groups(album)
    for group in groups:
        doc_pic_groups = group.get_doctor_pics(job, request.user)
        for doc_pic_group in doc_pic_groups:
            dpg = doc_pic_group.get_view_model(request.user, job)
            if dpg is not None:
                doc_pic_groups_ret.append(dpg)

    return doc_pic_groups_ret

def prepPics(album):
    pics_ret = []

    groups = Group.get_album_groups(album)
    for group in groups:
        pics = Pic.get_group_pics(group)
        for pic in pics:
            pics_ret.append(pic.get_view_model(True))

    return pics_ret

def prepMessages(groups, album, request):
    messages_ret = []
    profile = request.user
    job = album.get_job_or_None()

    # TODO make sure this is valid, what if profile is null
    # and userprofile is null, hmmmm????????
    can_view_messages = profile == album.userprofile or \
                        (job and profile == job.doctor) or \
                        (profile and hasattr(profile, 'isa') and profile.isa('moderator'))

    if can_view_messages:
        for group in groups:
            message_ids = group['messages'] = []
            messages =  build_messages(GroupMessage.get_messages(group['id']), profile)

            for message in messages:
                message_ids.append(message['id'])
                messages_ret.append(message)

    return messages_ret

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


@require_login_as(['skaa', 'doctor'])
def messages_endpoint(request):
    result = {}
    if request.method == 'POST':
        original_json = simplejson.loads(request.body)
        data = original_json['message']
        message = data['message'].strip()
        job_val = data['job']
        if job_val != None:
            job_val = job_val.strip()
        group_val = data['group'].strip()
        msg = generate_message(request, message, job_val, group_val)
        data['id'] = msg.id
        result = original_json

    return json_result(result)

@require_login_as(['skaa', 'doctor'])
def email_config_endpoint(request, user_id):
    result = {
        'emailConfig' : {
            'id':                 request.user.id,
            'job_status_change':  True,
            'jobs_available':     True,
            'jobs_need_approval': False,
            'job_reminder':       True,
            'job_message':        True,
            'job_rejection':      True,
            'job_switched':       True,
        }
    }
    return json_result(result)

