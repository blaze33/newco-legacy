from django.conf import settings
from django.contrib.auth.signals import user_logged_in
from django.db.models.loading import get_model
from django.dispatch import receiver

import urlparse
from redis_completion import RedisEngine


def load_object(request):
    app_label = request.POST['app_label']
    object_name = request.POST['object_name']
    object_id = request.POST['id']
    model = get_model(app_label, object_name)

    lookup_kwargs = {'%s__exact' % model._meta.pk.name: object_id}

    try:
        return model._default_manager.get(**lookup_kwargs)
    except ObjectDoesNotExist:
        raise AttributeError('No %s for %s.' % (model._meta.app_label,
                                                lookup_kwargs))


def load_redis_engine():
    redis_url = urlparse.urlparse(settings.REDISTOGO_URL)
    if redis_url.scheme == "redis":
        return RedisEngine(host=redis_url.hostname, port=redis_url.port,
                                                password=redis_url.password)


@receiver(user_logged_in)
def update_redis(sender, request, user, **kwargs):
    pass
