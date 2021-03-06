from defaults import *
from settings.functions import get_cfg_setting
import os

DEPLOY_TYPE='PRODUCTION' # useful for logs, stack traces
DEBUG = False
IS_PRODUCTION = True # used to toggle things that don't go on the non-live site
# TODO: When we go live, get rid of this.
PRODUCTION_TESTING = False# used to add debug code to production when it isn't really production. ugh. confusing.

# TODO: Use debug keys with live keys:
#BALANCED_API_KEY_SECRET = 'ak-test-1MjuXmDfjhvI5VevnXBL9jsmSbaQwDXCu'
#BALANCED_MARKETPLACE_URI = '/v1/marketplaces/TEST-MP4dltaHHyJdwcMGTDAHbed4'
BALANCED_API_KEY_SECRET = 'ak-prod-2yf2rgaVWcYuDtDZlZgx8XkK2DQxN3cur'
BALANCED_MARKETPLACE_URI = '/v1/marketplaces/MP2Y5DANQ7F1xePOvEzdy88i'

STRIPE_SECRET_KEY = 'sk_live_4MyBlP6Pc09zR6VXHwMOpsYS' # live secret key
STRIPE_PUBLISHABLE_KEY = 'pk_live_4MyBok4dMfFRuek4mzQGXTEG' # live publishable key

# application id for stripe connect
STRIPE_CLIENT_ID='ca_4L1G0aOXIcIECm9MUTYXjonfhLEOqQ88'
AWS_ACCESS_KEY_ID = 'AKIAILOZZ7ACZPM7RVAQ'
AWS_SECRET_ACCESS_KEY = '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'
AWS_STORAGE_BUCKET_NAME = 'picdoctors_media'

DATABASES = {
    'default': {
        'ENGINE'   : 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'HOST'     : 'pd-production.c9b9prnejh0e.us-east-1.rds.amazonaws.com',
        'PORT'     : '5432',
        'NAME'     : 'picdoctors', # db name
        'USER'     : 'picdoctors',
        'PASSWORD' : '39HOzWv2w6dCfpqp7RexTQb47VpndzHG',
    }
}

ALLOWED_HOSTS = [ 'www.picdoctors.com', 'picdoctors.com' ]

SITE_URL = 'https://www.picdoctors.com'
STATIC_URL = 'https://d1136bh4kfiso6.cloudfront.net/static/' # cloudfront CDN

# apparently DJANGO isn't smart enough to figure out https if you are using a proxy to fake https
SECURE_PROXY_SSL_HEADER = ('wsgi.url_scheme', 'https')

path = os.path.join(PROJECT_ROOT, "settings/production.cfg")
SHA = get_cfg_setting(path, "sha") # useful in stack traces

#swap out debug versions of code for production releases
ReplaceJsFile(PIPELINE_JS['ember_libs']['source_filenames'], 'third_party/js/ember.js','third_party/js/ember.prod.js')

