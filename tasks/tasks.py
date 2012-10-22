from celery import task
from common.models import Pic
from annoying.functions import get_object_or_None

from common.models import Group
from skaa.picmask import generate_watermarked_image
from django.core.files.uploadedfile import InMemoryUploadedFile
from PIL import Image
from StringIO import StringIO
import pdb

@task(ignore_result=True)
def sendAsyncEmail(msg):
    msg.send()

@task()
def savePic(pic_id, file):
    pic = get_object_or_None(id=pic_id)
    pic.set_file(file)
    pic.save()

@task()
def saveWatermark(group_id, str_io_pic):
    group = get_object_or_None(Group, id=group_id)
    opened_image = Image.open(str_io_pic)

    #this may be a problem, what if they don't send a jpg
    file = InMemoryUploadedFile(str_io_pic, None, 'original.jpg', 'image/jpeg',
                                          str_io_pic.len, None)
    pic = Pic(path_owner="doc")
    pic.set_file(file)
    pic.save()

    wm_file = generate_watermarked_image(opened_image, "some info")
    wm_stream = StringIO()
    wm_file.save(wm_stream, format='JPEG')

    wm_file = InMemoryUploadedFile(wm_stream, None, 'wm.jpg', 'image/jpeg',
                                          wm_stream.len, None)

    wm_pic = Pic(path_owner="doc", watermark=True)
    wm_pic.set_file(wm_file)
    wm_pic.save()

    #create a new entry in the DocPicGroup
    group.add_doctor_pic(pic, wm_pic)
