import math
from decimal import *
from common.models import UserProfile, Job


def calculate_job_payout(job, doc):
    #TODO figure out how valuable doc is, and generate a percent for them
    #if request.user.get_profile().is_cool_doctor or stupid
    #chop off extra half penny
    doctors_cut = Decimal(.5)
    return math.floor(100 * job.price * doctors_cut) / 100


