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

