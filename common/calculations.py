import math
from common.models import UserProfile, Job
import pdb

def calculate_job_payout(job, doc):
    ###  Calculate the payout in cents ### 

    #TODO figure out how valuable doc is, and generate a percent for them
    #if request.user.get_profile().is_cool_doctor or stupid
    #chop off extra half penny
    doctors_cut = .5
    return int(math.floor(job.price_cents * doctors_cut))


