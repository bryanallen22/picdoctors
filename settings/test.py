from defaults import *

from settings.functions import get_cfg_setting
import os

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

# As of Django 1.5, we have to declare the allowed hosts for security reasons.
# On a non production machine, that's annoying because we'd like to dial in
# directly through the IP address, so we add it here. Unfortunately, it's kinda
# clumsy because there's not a good way to figure out our external IP from
# the machine itself, so we had to write it as part of the deployment process.
path = os.path.join(PROJECT_ROOT, "settings/test.cfg")
external_ip = get_cfg_setting(path, "external_ip")
if external_ip:
    ALLOWED_HOSTS.append( external_ip )
