from django.db import models
from util.models import DeleteMixin
from upload.models import Batch

# Create your models here.
class Job(DeleteMixin):
    #Job status constants
    STATUS_USER_SUBMITTED = 'user_sub' #submitted to doctors
    STATUS_TOO_LOW   = 'too_low' #not worth doctors time
    STATUS_DOCTOR_ACCEPTED  = 'doctor_acc' #doctor accepted
    STATUS_DOCTOR_REQUESTS_ADDITIONAL_INFORMATION = 'doc_need_info'
    STATUS_DOCTOR_SUBMITTED = 'docter_sub' #submitted to user for approval
    STATUS_USER_ACCEPTED    = 'user_acc'   #user accepts the finished product
    STATUS_USER_REQUESTS_ADDITIONAL_WORK = 'user_add' #scope creep
    STATUS_USER_REJECTS     = 'user_rej'   #user rejects product and wants a refund...

    #Job status Choices for the job_status field below
    JOB_STATUS_CHOICES = (
        (STATUS_USER_SUBMITTED, 'User Submitted'),
        (STATUS_TOO_LOW, 'Price Too Low'),
        (STATUS_DOCTOR_ACCEPTED, 'Doctor Accepted Job'),
        (STATUS_DOCTOR_REQUESTS_ADDITIONAL_INFORMATION, 'Doctor Has Requested Additional Info'),
        (STATUS_DOCTOR_SUBMITTED, 'Doctor Submitted Work'),
        (STATUS_USER_ACCEPTED, 'User Accepted Work'),
        (STATUS_USER_REQUESTS_ADDITIONAL_WORK, 'User Has Requested Additional Work'),
        (STATUS_USER_REJECTS, 'User Has Rejected Work'),
    )

    #Never blank, no batch = no job. related_name since Batch already has a FK
    user_batch              = models.ForeignKey(Batch, 
                                                related_name='job_user_batch', 
                                                db_index=True)
    #This can be blank, doctor uploads batch later, related_name (see above)
    doctor_batch            = models.ForeignKey(Batch, 
                                                related_name='job_doctor_batch', 
                                                db_index=True, 
                                                blank=True, 
                                                null=True)
    #from something in the billions to 1 penny
    price                   = models.DecimalField(blank=False, 
                                                  max_digits=13, 
                                                  decimal_places=2)
# TODO implement Doctor class on top of django users class
#    doctor                  = models.ForeignKey(Doctor, blank=True, null=True)
    price_too_low_count     = models.IntegerField(blank=False, 
                                                  default=0)
    #max_length refers to the shorthand versions above
    job_status              = models.CharField(max_length=15, 
                                               choices=JOB_STATUS_CHOICES, 
                                               default=STATUS_USER_SUBMITTED)
