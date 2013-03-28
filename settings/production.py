from defaults import *

DEPLOY_TYPE='PRODUCTION' # useful for logs, stack traces
DEBUG = False
IS_PRODUCTION = True # used to toggle things that don't go on the non-live site

DATABASES = {
    'default': {

    }
}

AWS_ACCESS_KEY_ID = 'AKIAJ5JN3Q5MTH5LX6QQ'
AWS_SECRET_ACCESS_KEY = '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'
AWS_STORAGE_BUCKET_NAME = 'picdoctors_media'

# apparently DJANGO isn't smart enough to figure out https if you are using a proxy to fake https
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTOCOL', 'https')
