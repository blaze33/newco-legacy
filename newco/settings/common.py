# -*- coding: utf-8 -*-
### common.py
import sys
import os.path
import posixpath
import socket
from django.utils.translation import get_language_info

########## PATH CONFIGURATION
# Absolute filesystem path to this Django project directory.
PROJECT_ROOT = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

# Add all necessary filesystem paths to our system path so that we can use
# python import statements.
sys.path.append(os.path.normpath(os.path.join(PROJECT_ROOT, 'apps')))
########## END PATH CONFIGURATION

########## DEBUG CONFIGURATION
# Disable debugging by default.
DEBUG = False
TEMPLATE_DEBUG = DEBUG
########## END DEBUG CONFIGURATION

# tells Django to serve media through the staticfiles app.
SERVE_MEDIA = DEBUG

# django-compressor is turned off by default due to deployment overhead for
# most users. See <URL> for more information
COMPRESS = False

INTERNAL_IPS = [
    "127.0.0.1",
]

ADMINS = [
    # ("Your Name", "your_email@domain.com"),
]

MANAGERS = ADMINS

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = "Europe/Paris"

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = "fr"

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True
USE_TZ = True
USE_L10N = True

# Overrides full list for better perf
gettext_noop = lambda s: s
LANGUAGES = (
    ('en', gettext_noop('English')),
    ('fr', gettext_noop('French')),
)

# Where to look to compile translations
LOCALE_PATHS = (
    PROJECT_ROOT + '/locale',
    PROJECT_ROOT + '/apps/items/locale',
    PROJECT_ROOT + '/apps/affiliation/locale',
    PROJECT_ROOT + '/apps/dashboard/locale',
    PROJECT_ROOT + '/apps/profiles/locale',
    PROJECT_ROOT + '/apps/about/locale',
    PROJECT_ROOT + '/apps/custaccount/locale',
    PROJECT_ROOT + '/apps/utils/locale',
    PROJECT_ROOT + '/apps/utils/follow/locale',
    PROJECT_ROOT + '/apps/utils/help/locale',
    PROJECT_ROOT + '/apps/utils/vote/locale',
    PROJECT_ROOT + '/venv_locales/account/locale',
)

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(PROJECT_ROOT, "site_media", "media")

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = "/site_media/media/"

# Absolute path to the directory that holds static files like app media.
# Example: "/home/media/media.lawrence.com/apps/"
STATIC_ROOT = os.path.join(PROJECT_ROOT, "site_media", "static")

# URL that handles the static files like app media.
# Example: "http://media.lawrence.com"
STATIC_URL = "/site_media/static/"

# Additional directories which hold static files
STATICFILES_DIRS = [
    os.path.join(PROJECT_ROOT, "static"),
]

STATICFILES_FINDERS = [
    "staticfiles.finders.FileSystemFinder",
    "staticfiles.finders.AppDirectoriesFinder",
    "staticfiles.finders.LegacyAppDirectoriesFinder",
    "compressor.finders.CompressorFinder",
]

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = posixpath.join(STATIC_URL, "admin/")

# Subdirectory of COMPRESS_ROOT to store the cached media files in
COMPRESS_OUTPUT_DIR = "cache"

# Make this unique, and don't share it with anybody.
SECRET_KEY = "6)5+m(x@i@be*2y=je@+!yj_rt+=e_w4*1giv&aq7p%shrhy*a"

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = [
    "django.template.loaders.filesystem.Loader",
    "django.template.loaders.app_directories.Loader",
    'apptemplates.Loader',
]

MIDDLEWARE_CLASSES = [
    "django.middleware.gzip.GZipMiddleware",
    'htmlmin.middleware.HtmlMinifyMiddleware',
    "django.middleware.common.CommonMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django_openid.consumer.SessionConsumer",
    "django.contrib.messages.middleware.MessageMiddleware",
    "account.middleware.LocaleMiddleware",
    "account.middleware.TimezoneMiddleware",
    "pagination.middleware.PaginationMiddleware",
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    "utils.middleware.AjaxRedirectMiddleware",
]

HTML_MINIFY = False

SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"

ROOT_URLCONF = "newco.urls"

TEMPLATE_DIRS = [
    os.path.join(PROJECT_ROOT, "templates"),
]

TEMPLATE_CONTEXT_PROCESSORS = [
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.tz",
    "django.core.context_processors.request",
    "django.contrib.messages.context_processors.messages",

    "staticfiles.context_processors.static",

    "account.context_processors.account",
    "pinax_theme_bootstrap.context_processors.theme",

    "profiles.context_processors.profile",
    "utils.context_processors.mixpanel",
    "utils.context_processors.site",
    "utils.redis.context_processors.redis_url",
]

INSTALLED_APPS = [
    # Django
    # "admin_tools",
    # 'admin_tools.theming',
    # 'admin_tools.menu',
    # 'admin_tools.dashboard',
    "django_admin_bootstrapped",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sites",
    "django.contrib.messages",
    "django.contrib.humanize",
    "django.contrib.sitemaps",
    "account",

    # theme
    "django_forms_bootstrap",
    "pinax_theme_bootstrap",

    # external
    "staticfiles",
    "statici18n",
    "compressor",
    "django_openid",
    "timezones",
    "pagination",
    "idios",
    "metron",

    # Deployment
    "south",
    "gunicorn",
    "storages",

    # Monitoring
    "raven.contrib.django",

    # Project-external
    "newco_bw_editor",

    # Project
    "about",
    "affiliation",
    "custaccount",
    "dashboard",
    "items",
    "profiles",
    "utils",
    "utils.follow",
    "utils.help",
    "utils.hyphenate",
    "utils.redis",
    "utils.vote",
    "content",

    # Foreign apps
    "taggit",
    "voting",
    "follow",
    "gravatar",
    "tastypie",
    "amazonproduct",
    "softhyphen",
]

FIXTURE_DIRS = [
    os.path.join(PROJECT_ROOT, "fixtures"),
]

MESSAGE_STORAGE = "django.contrib.messages.storage.session.SessionStorage"

ABSOLUTE_URL_OVERRIDES = {
    "auth.user": lambda o: "/profiles/profile/%d/%s" %
                           (o.get_profile().pk, o.get_profile().slug),
}

AUTHENTICATION_BACKENDS = [
    'account.auth_backends.EmailAuthenticationBackend',
    'profiles.backends.ProfileBackend',
    'items.backends.ItemBackend',
]

AUTH_PROFILE_MODULE = "profiles.Profile"
NOTIFICATION_LANGUAGE_MODULE = "account.Account"

DEFAULT_FROM_EMAIL = 'feedback@newco-project.fr'

LOGIN_URL = "/account/login/"

# django-user-accounts
ACCOUNT_LOGIN_URL = "/account/login/"
ACCOUNT_OPEN_SIGNUP = True
ACCOUNT_CONTACT_EMAIL = False
ACCOUNT_EMAIL_UNIQUE = True
ACCOUNT_EMAIL_CONFIRMATION_REQUIRED = False
ACCOUNT_EMAIL_CONFIRMATION_EMAIL = True
ACCOUNT_CREATE_ON_SAVE = False
ACCOUNT_LOGIN_REDIRECT_URL = "/?welcome=back"
ACCOUNT_SIGNUP_REDIRECT_URL = "/?welcome=home"
ACCOUNT_LOGOUT_REDIRECT_URL = "/?welcome=logout"
ACCOUNT_USER_DISPLAY = lambda user: user.get_profile().name
ACCOUNT_LANGUAGES = [
    (code, get_language_info(code).get("name_local"))
    for code in ['fr', 'en']
]

# idios
IDIOS_USE_USERNAME = False

#Profile pictures
GRAVATAR_DEFAULT_IMAGE = 'identicon'

# AWS
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_ASSOCIATE_TAG = os.environ.get('AWS_ASSOCIATE_TAG')
AWS_LOCALE = os.environ.get('AWS_LOCALE')

# Amazon Product API because IAM credentials aren't working
AWS_PRODUCT_ACCESS_KEY_ID = os.environ.get('AWS_PRODUCT_ACCESS_KEY_ID')
AWS_PRODUCT_SECRET_ACCESS_KEY = os.environ.get('AWS_PRODUCT_SECRET_ACCESS_KEY')

# API services
GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
GOOGLE_SEARCH_ENGINE_ID = os.environ.get('GOOGLE_SEARCH_ENGINE_ID')

# Redis database ## redis://username:password@localhost:6379/0
REDISTOGO_URL = os.environ.get("REDISTOGO_URL")

# Voting
VOTING_ZERO_VOTES_ALLOWED = True

DEBUG_TOOLBAR_CONFIG = {
    "INTERCEPT_REDIRECTS": False,
}

SENTRY_DSN = os.environ.get('SENTRY_DSN')

# Mixpanel API
MIXPANEL_KEY_ID = os.environ.get('MIXPANEL_KEY_ID')
MIXPANEL_API_KEY = os.environ.get('MIXPANEL_API_KEY')
MIXPANEL_API_SECRET = os.environ.get('MIXPANEL_API_SECRET')
MIXPANEL_API_KEY_DEV = os.environ.get('MIXPANEL_API_KEY_DEV')
MIXPANEL_API_SECRET_DEV = os.environ.get('MIXPANEL_API_SECRET_DEV')

# django-taggit
TAGGIT_ENABLE_SPACE_SPLIT_IF_NOT_QUOTES = False
TAGGIT_FORCE_LOWERCASE = True
