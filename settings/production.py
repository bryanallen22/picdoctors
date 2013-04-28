from defaults import *
from settings.functions import get_cfg_setting
import os

DEPLOY_TYPE='PRODUCTION' # useful for logs, stack traces
DEBUG = False
IS_PRODUCTION = True # used to toggle things that don't go on the non-live site

# TODO: Use debug keys with live keys:
BALANCED_API_KEY_SECRET = '959cf402989b11e29955026ba7c1aba6'
BALANCED_MARKETPLACE_URI = '/v1/marketplaces/TEST-MP4yysJEaaWktNOnJGlPwHnc'

AWS_ACCESS_KEY_ID = 'AKIAJ5JN3Q5MTH5LX6QQ'
AWS_SECRET_ACCESS_KEY = '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'
AWS_STORAGE_BUCKET_NAME = 'picdoctors_media'

DATABASES = {
    'default': {
        'ENGINE'   : 'django.db.backends.mysql',
        'HOST'     : 'db0.c9b9prnejh0e.us-east-1.rds.amazonaws.com',
        'PORT'     : 3306,
        'NAME'     : 'picdoctors', # db name
        'USER'     : 'picdoctors',
        'PASSWORD' : 'cm9vJ2KUBjh8KQJ7',
    }
}

ALLOWED_HOSTS = [ 'www.picdoctors.com', 'picdoctors.com' ]

SITE_URL = 'https://www.picdoctors.com'

# apparently DJANGO isn't smart enough to figure out https if you are using a proxy to fake https
SECURE_PROXY_SSL_HEADER = ('wsgi.url_scheme', 'https')

path = os.path.join(PROJECT_ROOT, "settings/production.cfg")
SHA = get_cfg_setting(path, "sha") # useful in stack traces

