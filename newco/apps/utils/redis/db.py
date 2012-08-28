import redis
from django.conf import settings

redis = redis.from_url(settings.REDISTOGO_URL)
