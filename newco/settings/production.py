# -*- coding: utf-8 -*-
### production.py
from common import *
from postgresify import postgresify
import django_pylibmc
### other production-specific stuff

# memcache settings
MIDDLEWARE_CLASSES = [
    "django.middleware.cache.UpdateCacheMiddleware",
    "django.middleware.cache.FetchFromCacheMiddleware",
] + MIDDLEWARE_CLASSES

CACHES = {
    'default': {
        'BACKEND': 'django_pylibmc.memcached.PyLibMCCache'
    }
}

# S3 storage settings
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
STATICFILES_STORAGE = DEFAULT_FILE_STORAGE

AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')

STATIC_URL = '//s3.amazonaws.com/%s/' % AWS_STORAGE_BUCKET_NAME
ADMIN_MEDIA_PREFIX = STATIC_URL + 'admin/'
AWS_QUERYSTRING_AUTH = False # Don't include auth in every url

# Database settings will be overriden when deployed on Heroku
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3", # Add "postgresql_psycopg2", "postgresql", "mysql", "sqlite3" or "oracle".
        "NAME": "db-prod.db",                       # Or path to database file if using sqlite3 dev.db.
        "USER": "",                             # Not used with sqlite3.
        "PASSWORD": "",                         # Not used with sqlite3.
        "HOST": "",                             # Set to empty string for localhost. Not used with sqlite3.
        "PORT": "",                             # Set to empty string for default. Not used with sqlite3.
    }
}

HEROKU_DATABASES = postgresify()
if HEROKU_DATABASES:
    DATABASES = HEROKU_DATABASES
