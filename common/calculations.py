import math
from common.models import Job
import ipdb

def calculate_job_payout(job, profile):
    """
    Calculate how much this person gets paid for a given job.

    Return (payout_cents, tier)
    """
    ###  Calculate the payout in cents ###
    if not profile.isa('doctor'):
        return (0, 'N/A')

    doctors_cut = .5
    rating = profile.rating / 100.0

    # Get the number of pictures the doctor has produced in the last 30 days
    cnt = profile.get_approval_count()
    if cnt <= 19:
        doctors_cut = .5
        tier = 'Tier 1'
    elif cnt <= 39:
        doctors_cut = .55 + rating
        tier = 'Tier 2'
    elif cnt <= 69:
        doctors_cut = .60 + rating
        tier = 'Tier 3'
    elif cnt > 69:
        doctors_cut = .65 + rating
        tier = 'Tier 4'

    # If they have been special cased to have a hard coded payout
    # give it to them
    if profile.fixed_payout_pct > doctors_cut:
        doctors_cut = profile.fixed_payout_pct

    payout = int(math.floor(job.cents() * doctors_cut))
    return (payout, tier)
