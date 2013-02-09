import math
from common.models import UserProfile, Job, DoctorInfo
import pdb
import logging

def calculate_job_payout(job, doc):
    ###  Calculate the payout in cents ### 
    doc_info = DoctorInfo.get_docinfo_or_None(doc)
    if not doc_info:
        logging.error('unable to get docinfo for %s' % doc)
        return 0

    doctors_cut = .5
    
    cnt = doc_info.approval_count
    if cnt < 10:
        doctors_cut = .5
    elif cnt < 30:
        doctors_cut = .6
    elif cnt < 60:
        doctors_cut = .65
    elif cnt < 100:
        doctors_cut = .67
    elif cnt < 150:
        doctors_cut = .69
    elif cnt < 210:
        doctors_cut = .7
    elif cnt < 280:
        doctors_cut = .71
    elif cnt < 400:
        doctors_cut = .72
    elif cnt < 1000:
        doctors_cut = .75
    elif cnt >= 1000:
        doctors_cut = .8

    if cnt >= 10:
        doctors_cut += doc_info.rating
    
    return int(math.floor(job.bp_hold.cents * doctors_cut))


