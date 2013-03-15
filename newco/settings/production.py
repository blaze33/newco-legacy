# -*- coding: utf-8 -*-
### production.py
from common import *
from postgresify import postgresify
from memcacheify import memcacheify
### other production-specific stuff

# Default is empty list => everything is allowed.
# Only works in production. In debug, all hosts are allowed as well.
# Used if host is grabbed through get_host method of django.http.HttpRequest,
# not by 'request.META.HTTP_HOST'.
# ALLOWED_HOSTS = [
#     ".newco-project.fr",
#     ".newco-project.com",
#     "newco-staging.herokuapp.com",
#     "newco-project.s3.amazonaws.com",
# ]

# memcache settings
if os.environ.get('USE_MEMCACHE'):
    MIDDLEWARE_CLASSES = ["django.middleware.cache.UpdateCacheMiddleware",] + \
                         MIDDLEWARE_CLASSES + \
                         ["django.middleware.cache.FetchFromCacheMiddleware"]
    CACHES = memcacheify()
else:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'unique-snowflake'
        }
    }

# S3 storage settings
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
STATICFILES_STORAGE = DEFAULT_FILE_STORAGE

AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')

STATIC_URL = 'http://%s.s3.amazonaws.com/' % AWS_STORAGE_BUCKET_NAME
ADMIN_MEDIA_PREFIX = STATIC_URL + 'admin/'
AWS_S3_SECURE_URLS = False
AWS_QUERYSTRING_AUTH = False  # Don't include auth in every url
AWS_PRELOAD_METADATA = True  # fast sync, cf. http://stackoverflow.com/a/8440276/343834
# wait for release bump, cf. issue https://bitbucket.org/david/django-storages/issue/134/

# e-mail settings for sendgrid
EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_HOST_USER = os.environ.get('SENDGRID_USERNAME')
EMAIL_HOST_PASSWORD = os.environ.get('SENDGRID_PASSWORD')
EMAIL_PORT = 587
EMAIL_USE_TLS = True

HEROKU_DATABASES = postgresify()
if HEROKU_DATABASES:
    DATABASES = HEROKU_DATABASES
    DATABASES['default']['OPTIONS'] = {'autocommit': True}
    DATABASES['default']['ENGINE'] = 'django_hstore.postgresql_psycopg2'
    SOUTH_DATABASE_ADAPTERS = {'default': 'south.db.postgresql_psycopg2'}

########## Django compressor settings
AWS_IS_GZIPPED = True
# STATICFILES_STORAGE = 'newco.storage.CachedS3BotoStorage'
COMPRESS_URL = STATIC_URL
COMPRESS_STORAGE = STATICFILES_STORAGE
# COMPRESS_VERBOSE = True
# COMPRESS_ENABLED = True
# COMPRESS_OFFLINE = True

# use PROJECT_ROOT because django_compressor CssAbsoluteFilter works
# for files being in COMPRESS_ROOT
COMPRESS_ROOT = PROJECT_ROOT
# COMPRESS_ROOT = STATIC_ROOT

# S3 content expires 28 days later.
delay = 3600 * 24 * 28
AWS_HEADERS = {
    'Cache-Control': 'max-age={0}'.format(delay),
}
