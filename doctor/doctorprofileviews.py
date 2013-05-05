from annoying.decorators import render_to, ajax_request
from common.models import Profile

@render_to('doctor_profile.html')
def doctor_profile(request, nickname ):
    profile = Profile.objects.filter(nickname=nickname)
    
    if not profile:
        return { 'doctor_exists' : False }

    return {
            'doctor_exists' : True,
            'nickname'      : nickname,
            #'profile_url' : 'http://eofdreams.com/data_images/dreams/dog/dog-01.jpg',
    }

@ajax_request
def doctor_profile_pic(request):
    return {}

