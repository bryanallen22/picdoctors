from defaults import *

DEPLOY_TYPE='DEV' # useful for logs, stack traces
DEBUG = True 

# COMPRESS_ENABLED = True

IS_PRODUCTION = False # used to toggle things that don't go on the non-live site
BALANCED_API_KEY_SECRET = 'ak-test-1MjuXmDfjhvI5VevnXBL9jsmSbaQwDXCu'
BALANCED_MARKETPLACE_URI = '/v1/marketplaces/TEST-MP4dltaHHyJdwcMGTDAHbed4'

STRIPE_SECRET_KEY = 'sk_test_4MyBUlJBnpjULw8O0htBk20b' # test secret key
STRIPE_PUBLISHABLE_KEY = 'pk_test_4MyBHo1olVyt65ysLXn5BsyR' # test publishable key

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

#ignore the following error when using ipython:
#/django/db/backends/sqlite3/base.py:53: RuntimeWarning:
#"SQLite received a naive datetime (2012-11-02 11:20:15.156506) while time zone support is active."
#(This is only a problem on local dev, and it's only annoying, not a real problem.)
#See: http://stackoverflow.com/questions/14616805/why-wont-django-use-ipython
import warnings
import exceptions
warnings.filterwarnings("ignore", category=exceptions.RuntimeWarning, module='django.db.backends.sqlite3', lineno=53)

