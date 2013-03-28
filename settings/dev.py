from defaults import *

DEPLOY_TYPE='DEV' # useful for logs, stack traces
DEBUG = True
IS_PRODUCTION = False # used to toggle things that don't go on the non-live site
BALANCED_API_KEY_SECRET = '2726feb439f011e294b1026ba7f8ec28'
BALANCED_MARKETPLACE_URI = '/v1/marketplaces/TEST-MP1c0n2GjbjUEgctn32jYQE0'

AWS_ACCESS_KEY_ID = 'AKIAJYVA2NHBM5YJ3WWQ'
AWS_SECRET_ACCESS_KEY = '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'
AWS_STORAGE_BUCKET_NAME = 'picdoctors_nonproduction'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': '%s/sqlite.db' % PROJECT_ROOT, # Or path to database file if using sqlite3.
    }
}

SITE_URL = 'http://localhost:8000'

ALLOWED_HOSTS.append( 'localhost' )
ALLOWED_HOSTS.append( '127.0.0.1' )
