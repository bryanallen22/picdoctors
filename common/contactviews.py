from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.utils import simplejson

from annoying.decorators import render_to
from annoying.functions import get_object_or_None

from common.models import Job, Batch, Group, Pic
from common.models import JobMessage, GroupMessage
from common.functions import get_profile_or_None, get_time_string
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags


import pdb
import logging
import datetime

class Message():
    def __init__(self):
        self.commentor = None
        self.message = ''
        self.created = ''
        self.unseen = ''



class PicComment():
    def __init__(self):
        self.user_pics = []
        self.doc_pic = None
        self.messages = []
        self.group_id = -1




# still haven't tested it, the essential hope is the shared model
# will allow me to just send it in here and I can suck info out
def prep_messages(base_messages, profile, job):
    messages = []
    for msg in base_messages:
        message = Message()
        message.commentor = msg.commentor.user.username
        message.message = msg.message
        message.created = get_time_string(msg.created)
        messages.append(message.__dict__)
        if msg.skaa_viewed == False and job.skaa == profile:
            message.unseen = 'unseen'
            msg.skaa_viewed = True
            msg.save()

        if msg.doctor_viewed == False and job.doctor == profile:
            message.unseen = 'unseen'
            msg.doctor_viewed = True
            msg.save()


    return simplejson.dumps(messages)

@login_required
@render_to('contact.html')
def contact(request, job_id):
    #SECURITY (Move to Decorator)
    #############################
    profile = get_profile_or_None(request)

    job = get_object_or_None(Job, pk=job_id)

    if not job:
        return redirect('/')

    if job.skaa != profile and job.doctor != profile:
        return redirect('/')

    #############################
    #############################

    job_messages = prep_messages(JobMessage.get_messages(job), profile, job)

    groups = Group.get_batch_groups(job.batch)
    groupings = []
    for group in groups:
        picco = PicComment()
        picco.user_pics = Pic.get_group_pics(group)
        picco.group_id = group.id
        docPicGroup = group.get_latest_doctor_pic()
        if len(docPicGroup) > 0:
            docPicGroup = docPicGroup[0]
            picco.doc_pic = docPicGroup.get_pic()
        picco.messages = prep_messages(GroupMessage.get_messages(group), profile, job)
        groupings.append(picco)


    return {'job_id': job.id, 'job_messages' : job_messages, 'groupings' : groupings}

def can_add_message(request):
    return True

def message_handler(request):
    result = {}
    if request.method == 'POST':
        data = simplejson.loads(request.body)
        message = data['message'].strip()
        if can_add_message(request) and message != '':
            profile = get_profile_or_None(request)
            msg = None
            group_val = data['group_id'].strip()
            job_val = data['job_id'].strip()

            job = get_object_or_None(Job, id=int(job_val))

            if group_val != '':
                group = get_object_or_None(Group, id=int(group_val))
                msg = GroupMessage()
                msg.group = group
            else:
                msg = JobMessage()
                msg.job = job

            msg.message = message
            msg.commentor = profile
            if job.skaa == profile:
                msg.skaa_viewed = True
            elif job.doctor == profile:
                msg.doctor_viewed = True
            msg.save()

            generate_message_email(job, profile, message)


    response_data = simplejson.dumps(result)
    return HttpResponse(response_data, mimetype='application/json')


def generate_message_email(job, profile, message):
    try:
        from_whom = 'User'
        to_email = job.doctor.user.email


        if job.doctor == profile:
            from_whom = 'Doctor'
            other_user_email = job.skaa.user.email

        subject = 'The ' + from_whom + ' commented on your job'
        #Do I want to send the message to them, or make them go to the page?a
        args = {'from_whom':from_whom, 'job_id':job.id} 
        html_content = render_to_string('contact_email.html', args)
                                        
        
        # this strips the html, so people will have the text
        text_content = strip_tags(html_content) 
        # create the email, and attach the HTML version as well.
        msg = EmailMultiAlternatives(subject, text_content, 'donotreply@picdoctors.com', [to_email])
        msg.attach_alternative(html_content, "text/html")
        msg.send()

#        send_mail(subject, message , 'donotreply@picdoctors.com', [other_user_email], fail_silently=False)
    except Exception as ex:
        raise ex

