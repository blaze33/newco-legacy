TWITTER_CONSUMER_KEY              = ''
TWITTER_CONSUMER_SECRET           = ''
FACEBOOK_APP_ID                   = ''
FACEBOOK_API_SECRET               = ''
LINKEDIN_CONSUMER_KEY             = ''
LINKEDIN_CONSUMER_SECRET          = ''
ORKUT_CONSUMER_KEY                = ''
ORKUT_CONSUMER_SECRET             = ''
GOOGLE_OAUTH2_CLIENT_ID           = '281591548397.apps.googleusercontent.com'
GOOGLE_OAUTH2_CLIENT_SECRET       = 'm1QGg10CHipIKGDQoov-1ZeL'
SOCIAL_AUTH_CREATE_USERS          = True
SOCIAL_AUTH_FORCE_RANDOM_USERNAME = True
SOCIAL_AUTH_DEFAULT_USERNAME      = 'socialauth_user'
SOCIAL_AUTH_COMPLETE_URL_NAME     = 'socialauth_complete'
#SOCIAL_AUTH_USER_MODEL            = 'socauth.CustomUser'
SOCIAL_AUTH_ERROR_KEY             = 'socialauth_error'
GITHUB_APP_ID                     = ''
GITHUB_API_SECRET                 = ''
FOURSQUARE_CONSUMER_KEY           = ''
FOURSQUARE_CONSUMER_SECRET        = ''


SOCIAL_AUTH_PIPELINE = [
    'social_auth.backends.pipeline.social.social_auth_user',
    'social_auth.backends.pipeline.associate.associate_by_email',
    'social_auth.backends.pipeline.misc.save_status_to_session',
    'socauth.pipeline.redirect_to_form',
    'socauth.pipeline.username',
    'social_auth.backends.pipeline.user.create_user',
    'social_auth.backends.pipeline.social.associate_user',
    'social_auth.backends.pipeline.social.load_extra_data',
    'social_auth.backends.pipeline.user.update_user_details',
]

SOCIAL_AUTH_UUID_LENGTH = 16