# -*- coding: utf-8 -*-
### production.py
from common import *
from postgresify import postgresify
from memcacheify import memcacheify
import django_pylibmc
### other production-specific stuff

# serving gzipped content
MIDDLEWARE_CLASSES = ["django.middleware.gzip.GZipMiddleware"] + \
                         MIDDLEWARE_CLASSES

# memcache settings
if os.environ.get('USE_MEMCACHE'):
    MIDDLEWARE_CLASSES = ["django.middleware.cache.UpdateCacheMiddleware",] + \
                         MIDDLEWARE_CLASSES + \
                         ["django.middleware.cache.FetchFromCacheMiddleware"]
    CACHES = memcacheify()

# S3 storage settings
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
STATICFILES_STORAGE = DEFAULT_FILE_STORAGE

AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')

STATIC_URL = '//s3.amazonaws.com/%s/' % AWS_STORAGE_BUCKET_NAME
ADMIN_MEDIA_PREFIX = STATIC_URL + 'admin/'
AWS_QUERYSTRING_AUTH = False  # Don't include auth in every url

# e-mail settings for sendgrid
EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_HOST_USER = os.environ.get('SENDGRID_USERNAME')
EMAIL_HOST_PASSWORD = os.environ.get('SENDGRID_PASSWORD')
EMAIL_PORT = 587
EMAIL_USE_TLS = True

# Database settings will be overriden when deployed on Heroku
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3", # Add "postgresql_psycopg2", "postgresql", "mysql", "sqlite3" or "oracle".
        "NAME": "db-prod.db",                   # Or path to database file if using sqlite3 dev.db.
        "USER": "",                             # Not used with sqlite3.
        "PASSWORD": "",                         # Not used with sqlite3.
        "HOST": "",                             # Set to empty string for localhost. Not used with sqlite3.
        "PORT": "",                             # Set to empty string for default. Not used with sqlite3.
    }
}

HEROKU_DATABASES = postgresify()
if HEROKU_DATABASES:
    DATABASES = HEROKU_DATABASES
    DATABASES['default']['OPTIONS'] = {'autocommit': True}
    DATABASES['default']['ENGINE'] = 'django_hstore.postgresql_psycopg2'
    SOUTH_DATABASE_ADAPTERS = {'default': 'south.db.postgresql_psycopg2'}
