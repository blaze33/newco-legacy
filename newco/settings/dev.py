# -*- coding: utf-8 -*-
### dev.py
from common import *
from postgresify import postgresify
DEBUG = True
### other development-specific stuff

# tells Pinax to serve media through the staticfiles app.
SERVE_MEDIA = DEBUG

# Database settings will be overriden when deployed on Heroku
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3", # Add "postgresql_psycopg2", "postgresql", "mysql", "sqlite3" or "oracle".
        "NAME": "db-dev.db",                       # Or path to database file if using sqlite3 dev.db.
        "USER": "",                             # Not used with sqlite3.
        "PASSWORD": "",                         # Not used with sqlite3.
        "HOST": "",                             # Set to empty string for localhost. Not used with sqlite3.
        "PORT": "",                             # Set to empty string for default. Not used with sqlite3.
    }
}

EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'newco.project.dev@gmail.com'
EMAIL_HOST_PASSWORD = '!Password1'
EMAIL_PORT = 587
EMAIL_USE_TLS = True

HEROKU_DATABASES = postgresify()
if HEROKU_DATABASES:
    DATABASES = HEROKU_DATABASES
