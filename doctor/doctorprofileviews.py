from annoying.decorators import render_to, ajax_request
from annoying.functions import get_object_or_None
from common.models import Profile, Job, Pic

def get_job_summary(job):
    """
    Get some kind of link text associated with the job. Just grab the first
    Pic associated with this job and get it's general description
    """
    ret = None

    pics = Pic.objects.filter(album=job.album).order_by('group')

    for pic in pics:
        if pic.general_instructions:
            ret = pic.general_instructions
            break

    return ret or "No description available"

@render_to('doctor_profile.html')
def doctor_profile(request, nickname ):
    profile = get_object_or_None(Profile, nickname=nickname)
    
    if not profile:
        return { 'doctor_exists' : False }

    profile_pic_url = None
    if profile.pic:
        profile_pic_url = profile.pic.get_preview_url()

    jobs = Job.objects.filter(doctor=profile).order_by('created').reverse()
    jobs = [ (j,get_job_summary(j)) for j in jobs if j.album.allow_publicly]

    return {
            'doctor_exists'     : True,
            'nickname'          : nickname,
            'profile_pic_url'   : profile_pic_url,
            'doc_profile_desc'  : profile.doc_profile_desc,
            'jobs'              : jobs,
    }

