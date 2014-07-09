from defaults import *

from settings.functions import get_cfg_setting
import os

DEPLOY_TYPE='TEST' # useful for logs, stack traces
DEBUG = False
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
        'ENGINE'   : 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME'     : 'picdoctors',                             # Or path to database file if using sqlite3.
        'USER'     : 'picdoctors',                             # Not used with sqlite3.
        'PASSWORD' : 'asdf',                                   # Not used with sqlite3.
        'HOST'     : '127.0.0.1',                              # Set to empty string for localhost. Not used with sqlite3.
        'PORT'     : '5432',                                   # Set to empty string for default. Not used with sqlite3.
    }
}

# As of Django 1.5, we have to declare the allowed hosts for security reasons.
# On a non production machine, that's annoying because we'd like to dial in
# directly through the IP address, so we add it here. Unfortunately, it's kinda
# clumsy because there's not a good way to figure out our external IP from
# the machine itself, so we had to write it as part of the deployment process.
path = os.path.join(PROJECT_ROOT, "settings/test.cfg")
external_ip = get_cfg_setting(path, "external_ip")
if external_ip:
    ALLOWED_HOSTS.insert(0, external_ip )

SITE_URL = 'https://' + external_ip

# apparently DJANGO isn't smart enough to figure out https if you are using a proxy to fake https
SECURE_PROXY_SSL_HEADER = ('wsgi.url_scheme', 'https')

SHA = get_cfg_setting(path, "sha") # useful in stack traces
