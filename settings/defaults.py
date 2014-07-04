# Django settings for picdoctors project.
import os
import djcelery
import sys

def ReplaceJsFile(items, old, new):
    for index, obj in enumerate(items):
        if obj == old:
            items[index] = new
            break

# PROJECT_ROOT is up a directory ( use dirname on this file twice )
PROJECT_ROOT = os.path.abspath( os.path.dirname(os.path.dirname(__file__)) )

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
    ('Bryan', 'bryan@picdoctors.com'),
    ('Daniel', 'daniel@picdoctors.com'),
)
SERVER_EMAIL='django@picdoctors.com'

MANAGERS = ADMINS


EXAMPLE_DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': os.path.join(PROJECT_ROOT, 'sqlite.db'), # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

# User Model
AUTH_USER_MODEL = 'common.Profile'

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = os.path.join(PROJECT_ROOT, 'media/')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/site_media/'

# URL prefix for admin static files -- CSS, JavaScript and images.
# Make sure to use a trailing slash.
# Examples: "http://foo.com/static/admin/", "/static/admin/".
ADMIN_MEDIA_PREFIX = '/static/admin/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(PROJECT_ROOT, 'static'),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'q^b*ga!8e3i_%2upa$_0iqpk7j(ni5ur^duf$+jy5^bsf21#s2'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware', # Typically should be last
    'basemiddleware.BaseMiddleware'
)

ROOT_URLCONF = 'urls'
WSGI_APPLICATION = 'wsgi.application'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.

    '%s/templates/'               % PROJECT_ROOT,
    '%s/templates/emails/'        % PROJECT_ROOT,
    '%s/templates/emails/skaa/'   % PROJECT_ROOT,
    '%s/templates/emails/doctor/' % PROJECT_ROOT,
    '%s/landings/html/'           % PROJECT_ROOT,
)

djcelery.setup_loader()
BROKER_HOST = 'localhost'
BROKER_PORT = 5672
BROKER_VHOST = 'carrot'
BROKER_USER = 'weliketoeat'
BROKER_PASSWORD = 'rabbitsfordinner'

# Migrateable Apps
PD_APPS = (
    'common',
    'skaa',
    'doctor',
    'messaging',
    'tasks',
    'notifications',
    'emailer',
    'handlebars_compiler'
)

# These are apps whose tests must pass before we can deploy.
# They are added to INSTALLED_APPS
TESTABLE_APPS = (
    'storages',
    'djcelery',
) + PD_APPS

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'django.contrib.humanize',
    'south',
    'pipeline',
    'debug_toolbar',
    'compressor',
    'seleniumtests',
    'django_extensions',
    'handlebars_compiler',
) + TESTABLE_APPS

from django.core.exceptions import SuspiciousOperation

def skip_suspicious_operations(record):
    if record.exc_info:
        exc_value = record.exc_info[1]
        if isinstance(exc_value, SuspiciousOperation):
            return False
    return True

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'standard': {
            'format' : "[%(asctime)s] %(levelname)s [%(pathname)s:%(lineno)s] %(message)s",
            'datefmt' : "%d/%b/%Y %H:%M:%S"
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        },
        'skip_suspicious_operations': {
            '()': 'django.utils.log.CallbackFilter',
            'callback': skip_suspicious_operations
        }
    },
    'handlers': {
        'null': {
            'level':'DEBUG',
            'class':'django.utils.log.NullHandler',
        },
        'logfile': {
            'level':'DEBUG',
            'class':'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/django/picdoctors.log',
            'maxBytes': 50000,
            'backupCount': 2,
            'formatter': 'standard',
        },
        'console':{
            'level':'INFO',
            'class':'logging.StreamHandler',
            'formatter': 'standard',
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django': {
            'handlers':['console', 'logfile', 'mail_admins'],
            'propagate': True,
            'level':'WARN',
        },
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'pd': {
            'handlers': ['console', 'logfile', 'mail_admins'],
            'level': 'DEBUG',
        },
    }
}

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static', # needed for {{ STATIC_URL }} in my templates
    'django.core.context_processors.request',
    'django.contrib.auth.context_processors.auth',
    'django.contrib.messages.context_processors.messages',
)


# django-storages -- used for S3
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
#AWS_CALLING_FORMAT = CallingFormat.SUBDOMAIN
AWS_HEADERS = {
    #'Expires': 'Thu, 15 Apr 2010 20:00:00 GMT',
    'Cache-Control': 'max-age=86400',
}

# This is required for debug_toolbar:
INTERNAL_IPS = ('127.0.0.1',)

EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_HOST_USER = 'picdoctors'
EMAIL_HOST_PASSWORD = 'USW6euCiIbUSxnqi'
EMAIL_PORT = 587
EMAIL_USE_TLS = True

# used by @require_login_as
LOGIN_URL='/signin/'

DEBUG_TOOLBAR_CONFIG = {
   'INTERCEPT_REDIRECTS': False,
}

# In nginx we should forward one of these to the other, but I'd rather be a bit permissive here and allow both
ALLOWED_HOSTS = [ 'picdoctors.com', 'www.picdoctors.com' ]

SITE_URL = 'https://www.picdoctors.com'


# compiler for Ember templates
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    # other finders..
    'compressor.finders.CompressorFinder',
)

COMPRESS_PRECOMPILERS = (
    ('text/x-handlebars', 'django-ember-precompile {infile}'),
)
# end pre-compiler for ember templates

PIPELINE_CSS = {
    'all_css': {
        'source_filenames': (
            # Paths are relative to settings.STATICFILES_DIRS!

            ###########
            # Libraries
            ###########
            'third_party/twitter-bootstrap/bootstrap/css/bootstrap.min.css',
            'third_party/rating/jquery.rating.css',

            ###########
            # Our stuff
            ###########
            'css/picdoctors.css',
            'css/spinner.css',
            'css/isotope.css',
            'css/qbeforeafter.css'
        ),
        'output_filename': 'compressed/all.css',
    },
}

PIPELINE_YUGLIFY_BINARY = os.path.join(PROJECT_ROOT, 'node_modules/yuglify/bin/yuglify')
PIPELINE_JS_COMPRESSOR = 'pipeline.compressors.slimit.SlimItCompressor'

PIPELINE_JS = {
    'all_js': {
        'source_filenames': [
            # Paths are relative to settings.STATICFILES_DIRS!

            ###########
            # Libraries
            ###########
            'third_party/js/jquery-1.11.1.js',
            'third_party/js/underscore.min.js',
            'third_party/js/animatedcollapse.js',
            'third_party/js/backbone.min.js',
            'third_party/js/jquery.isotope.min.js',
            'third_party/js/jquery.qbeforeafter.js',
            'third_party/js/jquery-ui.min.js',
            'third_party/js/jquery.tmpl.min.js',
            'third_party/js/json2.js',
            'third_party/jquery-file-upload/jquery.ui.widget.js',
            'third_party/jquery-file-upload/jquery.fileupload.js',
            'third_party/jquery-file-upload/jquery.fileupload-ui.js',
            'third_party/jquery-file-upload/jquery.iframe-transport.js',
            'third_party/twitter-bootstrap/bootstrap/js/bootstrap.min.js',
            'third_party/bootstrap-tour/deps/jquery.cookie.js',
            'third_party/bootstrap-tour/bootstrap-tour.min.js',
            'third_party/rating/jquery.rating.js',
            'third_party/moment/moment.min.js',

            ###############
            # Ember Stuff #
            ###############
            'third_party/js/handlebars-v1.3.0.js',
            'third_party/js/handlebars-fix.js',
            # this is the debug build, I want a way to say in debug use this
            'third_party/js/ember.js',
            'third_party/js/ember-data.js',

            ###########
            # Our stuff
            ###########
            'js/*.js',

            ###################
            # Our Ember Stuff #
            ###################
            'js/ember/application.js',
            'js/ember/router.js',
            'js/ember/helpers/*.js',
            'js/ember/mixins/*.js',
            'js/ember/models/*.js',
            'js/ember/routes/*.js',
            'js/ember/controllers/*.js',
            'js/ember/views/*.js',

            ##########
            # Logger #
            ##########
            'js/logger/*.js'

        ],
        'output_filename': 'compressed/all.js',
    }
}

HANDLEBARS_FOLDER = os.path.join(PROJECT_ROOT, 'static/js/ember/templates/')

STATICFILES_STORAGE = 'pipeline.storage.PipelineCachedStorage'

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = os.path.join(PROJECT_ROOT, 'static_out')

STRIPE_CLIENT_ID='ca_4L1GIZaGM721YBOx5HdrcRkofcNc3vwZ'
