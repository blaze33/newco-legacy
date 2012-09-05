import re
import unicodedata
import urlparse

from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from django.db.models import Q
from django.db.models.loading import get_model
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from django.contrib.auth.signals import user_logged_in
from django.contrib.contenttypes.models import ContentType

from taggit.models import Tag
from redis_completion import RedisEngine
from redis.exceptions import ConnectionError, RedisError

from items.models import Item
from profiles.models import Profile

PARAMS = {
    Item._meta.module_name: {
        "class": Item, "pk": "id", "title_field": "name",
        "recorded_fields": ["id", "name", "slug", "author", "pub_date"]
    },
    Profile._meta.module_name: {
        "class": Profile, "pk": "id", "title_field": "name",
        "recorded_fields": ["id", "name", "slug"]
    },
    Tag._meta.module_name: {
        "class": Tag, "pk": "id", "title_field": "name",
        "recorded_fields": ["id", "name", "slug"]
    },
}


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


def normalize_query(query_string,
                    findterms=re.compile(r'"([^"]+)"|(\S+)').findall,
                    normspace=re.compile(r'\s{2,}').sub):
    """
    Splits the query string in invidual keywords, getting rid of unecessary
    spaces and grouping quoted words together.

    Example::

        >>> normalize_query(' some random  words "with quotes  " and   spaces')
        ['some', 'random', 'words', 'with quotes', 'and', 'spaces']
    """

    return [normspace(' ', (t[0] or t[1]).strip()) \
                                            for t in findterms(query_string)]


def get_query(query_string, search_fields):
    """
    Returns a query, that is a combination of Q objects. That combination
    aims to search keywords within a model by testing the given search fields.
    """

    query = None
    terms = normalize_query(query_string)
    for term in terms:
        or_query = None
        for field_name in search_fields:
            q = Q(**{"%s__icontains" % field_name: term})
            if or_query is None:
                or_query = q
            else:
                or_query = or_query | q
        if query is None:
            query = or_query
        else:
            query = query & or_query
    return query


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
            raise RedisError("Redis Server URL is not valid.")
        else:
            return None


@receiver(user_logged_in)
def update_redis_db(sender, request, user, **kwargs):
    engine = load_redis_engine()

    if engine:
        for key, value in PARAMS.iteritems():
            cls = value["class"]
            ctype = ContentType.objects.get_for_model(cls)
            for obj in cls.objects.all():
                obj_id = obj.__getattribute__(value["pk"])
                title = obj.__getattribute__(value["title_field"])
                title = unicodedata.normalize('NFKD', title).encode('utf-8',
                                                                    'ignore')
                data = {"class": key, "title": title}
                for field in value["recorded_fields"]:
                    data.update({field: unicode(obj.__getattribute__(field))})
                engine.store_json(obj_id, title, data, ctype.id)


@receiver(post_save)
def redis_post_save(sender, instance=None, raw=False, **kwargs):
    mod_name = instance._meta.module_name
    if mod_name in PARAMS:
        engine = load_redis_engine()
        if engine:
            value = PARAMS[mod_name]

            obj_id = instance.__getattribute__(value["pk"])
            title = instance.__getattribute__(value["title_field"])
            title = unicodedata.normalize('NFKD', title).encode('utf-8',
                                                                'ignore')
            data = {"class": mod_name, "title": title}
            for field in value["recorded_fields"]:
                data.update({field: unicode(instance.__getattribute__(field))})
            ctype = ContentType.objects.get_for_model(instance)
            engine.store_json(obj_id, title, data, ctype.id)


@receiver(post_delete)
def redis_post_delete(sender, instance=None, **kwargs):
    mod_name = instance._meta.module_name
    if mod_name in PARAMS:
        engine = load_redis_engine()
        if engine:
            value = PARAMS[mod_name]

            obj_id = instance.__getattribute__(value["pk"])
            ctype = ContentType.objects.get_for_model(instance)
            engine.remove(obj_id, ctype.id)
