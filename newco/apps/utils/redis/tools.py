import unicodedata
import urlparse

from django.conf import settings
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from django.contrib.auth.signals import user_logged_in
from django.contrib.contenttypes.models import ContentType

from gravatar.templatetags.gravatar import gravatar_for_user
from redis_completion import RedisEngine
from redis.exceptions import ConnectionError, RedisError
from taggit.models import Tag

from items.models import Item
from profiles.models import Profile
from utils.tools import get_class_name

PARAMS = {
    get_class_name(Item): {
        "class": Item, "pk": "id", "title_field": "name", "text_field": "name",
        "recorded_fields": ["id", "name", "slug", "author", "pub_date"]
    },
    get_class_name(Profile): {
        "class": Profile, "pk": "id", "title_field": "name",
        "text_field": "name",
        "recorded_fields": ["id", "name", "slug", "about"],
        "fkey_fields": {
            "reputation": "user__reputation__reputation_incremented"},
        "extra_fields": ["gravatar_url"]
    },
    get_class_name(Tag): {
        "class": Tag, "pk": "id", "title_field": "name", "text_field": "name",
        "recorded_fields": ["id", "name", "slug"]
    },
}


def load_redis_engine():
    redis_url = urlparse.urlparse(settings.REDISTOGO_URL)
    if redis_url.scheme == "redis":
        engine = RedisEngine(host=redis_url.hostname, port=redis_url.port,
                             password=redis_url.password)
        try:
            info = engine.client.info()
            if "db0" in info:
                nb_keys = info["db0"]["keys"]
            else:
                nb_keys = 0
            print "Conn. Redis server, %s keys stored." % nb_keys
            return engine
        except ConnectionError:
            if settings.DEBUG:
                raise ConnectionError("Redis Server is not reachable.")
            else:
                return None
    else:
        if settings.DEBUG:
            raise RedisError("Redis Server '%s' URL is not valid."
                             % settings.REDISTOGO_URL)
        else:
            return None
engine = load_redis_engine()


def record_object(engine, obj, key, value, ctype=None):
    if ctype is None:
        ctype = ContentType.objects.get_for_model(obj)
    obj_id = obj.__getattribute__(value["pk"])
    title = obj.__getattribute__(value["title_field"])
    text = obj.__getattribute__(value["text_field"])
    if not title:
        return
    title = unicodedata.normalize("NFKD", title).encode("utf-8",
                                                        "ignore")
    text = unicodedata.normalize("NFKD", text).encode("utf-8",
                                                      "ignore")
    data = {"class": key, "title": title, "text": text}
    for field in value["recorded_fields"]:
        attr = obj.__getattribute__(field)
        unicode_attr = unicode(attr) if attr is not None else u""
        data.update({field: unicode_attr})
    for field_name, fkey_field in value.get("fkey_fields", {}).items():
        attr = get_fkey_attr(obj, fkey_field)
        unicode_attr = unicode(attr) if attr is not None else u""
        data.update({field_name: unicode_attr})
    for field in value.get("extra_fields", []):
        if field == "gravatar_url":
            data.update({field: unicode(gravatar_for_user(obj.user))})

    engine.store_json(obj_id, title, data, ctype.id)


@receiver(user_logged_in)
def update_redis_db(sender, request, user, **kwargs):
    if engine is None:
        return
    engine.flush(everything=True)
    for key, value in PARAMS.iteritems():
        # TODO: grouped query
        ctype = ContentType.objects.get_for_model(value["class"])
        for obj in value["class"].objects.select_related():
            record_object(engine, obj, key, value, ctype)


@receiver(post_save)
def redis_post_save(sender, instance=None, raw=False, **kwargs):
    key = "%s.%s" % (instance.__module__, instance._meta.object_name)
    if not key in PARAMS or engine is None:
        return
    record_object(engine, instance, key, PARAMS[key])


@receiver(post_delete)
def redis_post_delete(sender, instance=None, **kwargs):
    key = "%s.%s" % (instance.__module__, instance._meta.object_name)
    if not key in PARAMS or engine is None:
        return
    value = PARAMS[key]
    obj_id = instance.__getattribute__(value["pk"])
    ctype = ContentType.objects.get_for_model(instance)
    engine.remove(obj_id, ctype.id)


def get_fkey_attr(obj, field_name):
    val = obj
    for part in field_name.split('__'):
        val = getattr(val, part)
    return val
