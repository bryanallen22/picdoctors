import math
from common.models import Job
import ipdb
import logging

def calculate_job_payout(job, profile):
    ###  Calculate the payout in cents ### 
    if not profile.isa('doctor'):
        return 0

    doctors_cut = .5
    rating = profile.rating / 100.0
    
    cnt = profile.get_approval_count()
    if cnt < 19:
        doctors_cut = .5
    elif cnt < 39:
        doctors_cut = .55 + rating
    elif cnt < 69:
        doctors_cut = .60 + rating
    elif cnt > 69:
        doctors_cut = .65 + rating
    
    return int(math.floor(job.bp_hold.cents * doctors_cut))


