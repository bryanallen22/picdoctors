from annoying.decorators import render_to, ajax_request
from annoying.functions import get_object_or_None
from common.models import Profile

@render_to('doctor_profile.html')
def doctor_profile(request, nickname ):
    profile = get_object_or_None(Profile, nickname=nickname)
    
    if not profile:
        return { 'doctor_exists' : False }

    return {
            'doctor_exists'     : True,
            'nickname'          : nickname,
            'profile_pic_url'   : profile.pic.get_preview_url(),
            'doc_profile_desc'  : profile.doc_profile_desc
    }

