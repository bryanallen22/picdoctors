from defaults import *

DEPLOY_TYPE='TEST' # useful for logs, stack traces
DEBUG = False
IS_PRODUCTION = False # used to toggle things that don't go on the non-live site
BALANCED_API_KEY_SECRET = '2726feb439f011e294b1026ba7f8ec28'
BALANCED_MARKETPLACE_URI = '/v1/marketplaces/TEST-MP1c0n2GjbjUEgctn32jYQE0'

AWS_ACCESS_KEY_ID = 'AKIAIXCLPXQHNZTMBRXQ'
AWS_SECRET_ACCESS_KEY = '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'
AWS_STORAGE_BUCKET_NAME = 'picdoctors'

DATABASES = {
    'default': {
        'ENGINE'   : 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME'     : 'picdoctors',               # Or path to database file if using sqlite3.
        'USER'     : 'root',                     # Not used with sqlite3.
        'PASSWORD' : 'asdf',                     # Not used with sqlite3.
        'HOST'     : '',                         # Set to empty string for localhost. Not used with sqlite3.
        'PORT'     : '',                         # Set to empty string for default. Not used with sqlite3.
    }
}

# I might throw some if not production just find out what host:port we're running on
EMAIL_DOMAIN = 'localhost:8000'
