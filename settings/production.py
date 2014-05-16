from defaults import *
from settings.functions import get_cfg_setting
import os

DEPLOY_TYPE='PRODUCTION' # useful for logs, stack traces
DEBUG = False
IS_PRODUCTION = True # used to toggle things that don't go on the non-live site
# TODO: When we go live, get rid of this.
PRODUCTION_TESTING = True# used to add debug code to production when it isn't really production. ugh. confusing.

# TODO: Use debug keys with live keys:
BALANCED_API_KEY_SECRET = 'ak-test-1MjuXmDfjhvI5VevnXBL9jsmSbaQwDXCu'
BALANCED_MARKETPLACE_URI = '/v1/marketplaces/TEST-MP4dltaHHyJdwcMGTDAHbed4'

AWS_ACCESS_KEY_ID = 'AKIAJ5JN3Q5MTH5LX6QQ'
AWS_SECRET_ACCESS_KEY = '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'
AWS_STORAGE_BUCKET_NAME = 'picdoctors_media'

DATABASES = {
    'default': {
        'ENGINE'   : 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'HOST'     : 'picdoc-pg-production.c9b9prnejh0e.us-east-1.rds.amazonaws.com',
        'PORT'     : '5432',
        'NAME'     : 'picdoctors', # db name
        'USER'     : 'picdoctors',
        'PASSWORD' : 'b8vHqpgLcegYA5cV',
    }
}

ALLOWED_HOSTS = [ 'www.picdoctors.com', 'picdoctors.com' ]

SITE_URL = 'https://www.picdoctors.com'

# apparently DJANGO isn't smart enough to figure out https if you are using a proxy to fake https
SECURE_PROXY_SSL_HEADER = ('wsgi.url_scheme', 'https')

path = os.path.join(PROJECT_ROOT, "settings/production.cfg")
SHA = get_cfg_setting(path, "sha") # useful in stack traces

