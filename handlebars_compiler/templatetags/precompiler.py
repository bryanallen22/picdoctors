from django import template
from django.conf import settings
import os

register = template.Library()

@register.simple_tag
def insert_templates():
    return get_directory(settings.HANDLEBARS_FOLDER,[])

def get_directory(directory, parent):
    templates = ""
    for folder in get_immediate_subdirectories(directory):
        realFolder = os.path.join(directory, folder)
        newParent = list(parent)
        newParent.append(folder)
        templates += get_directory(realFolder, newParent)

    for file in os.listdir(directory):
        if file.endswith(".hbs"):
            partsOfName = list(parent)
            partsOfName.append(os.path.splitext(file)[0])
            name = '/'.join(partsOfName)
            filePath = os.path.join(directory, file)

            template = ""
            template = "\n\n\n<script "
            template += "type='text/x-handlebars' "
            template += "data-template-name='"
            template += name + "'>"

            #template += directory
                
            with open (filePath, "r") as templateFile:
                template += templateFile.read()
            template += "</script>\n"
            templates += template

    return templates

def get_immediate_subdirectories(dir):
    return [name for name in os.listdir(dir)
        if os.path.isdir(os.path.join(dir, name))]
