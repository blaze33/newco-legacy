# -*- coding: utf-8 -*-
### dev.py
from common import *
from postgresify import postgresify
DEBUG = True
### other development-specific stuff

# tells Pinax to serve media through the staticfiles app.
SERVE_MEDIA = DEBUG

# add development applications
INSTALLED_APPS += [
    "django_extensions",
    "debug_toolbar",
    "rosetta",
]

# Database settings will be overriden when deployed on Heroku
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3", # Add "postgresql_psycopg2", "postgresql", "mysql", "sqlite3" or "oracle".
        "NAME": "db-dev.db",                    # Or path to database file if using sqlite3 dev.db.
        "USER": "",                             # Not used with sqlite3.
        "PASSWORD": "",                         # Not used with sqlite3.
        "HOST": "",                             # Set to empty string for localhost. Not used with sqlite3.
        "PORT": "",                             # Set to empty string for default. Not used with sqlite3.
    },
    "slave": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": "db-dev.db",
        "TEST_MIRROR": "default"
    }
}

EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'newco.project.dev@gmail.com'
EMAIL_HOST_PASSWORD = '!Password1'
EMAIL_PORT = 587
EMAIL_USE_TLS = True

# When running WSGI daemon mode, using mod_wsgi 2.0c5 or later, this setting
# controls whether the contents of the gettext catalog files should be
# automatically reloaded by the WSGI processes each time they are modified.
# For performance reasons, this setting should be disabled in production
# environments.
ROSETTA_WSGI_AUTO_RELOAD = True
ROSETTA_UWSGI_AUTO_RELOAD = True
ROSETTA_MESSAGES_PER_PAGE = 50
ROSETTA_STORAGE_CLASS = 'rosetta.storage.CacheRosettaStorage'

HEROKU_DATABASES = postgresify()
if HEROKU_DATABASES:
    DATABASES = HEROKU_DATABASES
    DATABASES['default']['ENGINE'] = 'django_hstore.postgresql_psycopg2'
    SOUTH_DATABASE_ADAPTERS = {'default': 'south.db.postgresql_psycopg2'}

