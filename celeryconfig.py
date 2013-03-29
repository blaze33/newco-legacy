import os

if "dev" in os.environ.get("DJANGO_SETTINGS_MODULE"):
    REDIS_URL = os.environ.get("REDISCLOUD_URL", "redis://localhost:8888//")
    BROKER_URL = REDIS_URL
    CELERY_RESULT_BACKEND = REDIS_URL
else:
    # beware celery_redis_unixsocket use deprecated celery settings
    REDIS_SOCK = '/tmp/redis.sock'
    BROKER_TRANSPORT = 'celery_redis_unixsocket.broker.Transport'
    BROKER_HOST = REDIS_SOCK
    BROKER_VHOST = 0
    BROKER_PORT = 8888

    CELERY_RESULT_BACKEND = 'redisunixsocket'
    CELERY_REDIS_HOST = REDIS_SOCK
    CELERY_REDIS_VHOST = 0
    CELERY_REDIS_PORT = 8888

    import celery_redis_unixsocket
