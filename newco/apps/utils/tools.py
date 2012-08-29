from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from django.contrib.auth.signals import user_logged_in
from django.contrib.contenttypes.models import ContentType
from django.db.models.loading import get_model
from django.dispatch import receiver

from taggit.models import Tag
from items.models import Item
from profiles.models import Profile

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
    engine = load_redis_engine()
    print "Bonjour"

    params = {
        Item._meta.module_name: {
            "class": Item, "pk": "id", "title_field": "name",
            "recorded_fields": ["name", "slug", "author", "pub_date"]
        },
        Profile._meta.module_name: {
            "class": Profile, "pk": "id", "title_field": "name",
            "recorded_fields": ["name", "slug"]
        },
        Tag._meta.module_name: {
            "class": Tag, "pk": "id", "title_field": "name",
            "recorded_fields": ["name", "slug"]
        },
    }

    for key, value in params.iteritems():
        cls = value["class"]
        ctype = ContentType.objects.get(app_label=cls._meta.app_label,
                                            model=cls._meta.module_name)
        obj_ids = cls.objects.values_list(value["pk"], flat=True)
        for obj_id in obj_ids:
            obj = cls.objects.get(id=obj_id)
            title = unicode(obj.__getattribute__(value["title_field"]))
            data = {"class": key, "title": title}
            for field in value["recorded_fields"]:
                data.update({field: unicode(obj.__getattribute__(field))})
            engine.store_json(obj_id, title, data, ctype.id)
