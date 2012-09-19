import itertools
import re
import unicodedata
import urlparse

from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from django.db.models import Q, Sum
from django.db.models.loading import get_model
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from django.contrib.auth.signals import user_logged_in
from django.contrib.contenttypes.models import ContentType

from generic_aggregation import generic_annotate
from redis_completion import RedisEngine
from redis.exceptions import ConnectionError, RedisError
from taggit.models import Tag
from voting.models import Vote

from items.models import Item, Content
from profiles.models import Profile

PARAMS = {
    "%s.%s" % (Item.__module__, Item._meta.object_name): {
        "class": Item, "pk": "id", "title_field": "name",
        "recorded_fields": ["id", "name", "slug", "author", "pub_date"]
    },
    "%s.%s" % (Profile.__module__, Profile._meta.object_name): {
        "class": Profile, "pk": "id", "title_field": "name",
        "recorded_fields": ["id", "name", "slug"]
    },
    "%s.%s" % (Tag.__module__, Tag._meta.object_name): {
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


def get_query(query_string, search_fields, terms=None):
    """
    Returns a query, that is a combination of Q objects. That combination
    aims to search keywords within a model by testing the given search fields.
    """

    if not terms:
        terms = normalize_query(query_string)
    query = None
    for term in terms:
        or_query = None
        for field_name in search_fields:
            q = Q(**{"%s__icontains" % field_name: term})
            or_query = q if or_query is None else or_query | q
        query = or_query if query is None else query & or_query
    return query


def get_queries_by_score(query_string, search_fields):
    """
    Returns a list of queries, with each element being a combination of
    Q objects. That combination aims to search keywords within a model
    by testing the given search fields.
    """

    terms = normalize_query(query_string)
    query_dict = dict()
    for score in range(1, len(terms) + 1):
        queries = None
        term_combinations = itertools.combinations(terms, score)
        for term_combination in term_combinations:
            query = get_query("", search_fields, term_combination)
            queries = queries | (query) if queries is not None else (query)
        query_dict.update({score: queries})
    return query_dict


def get_sorted_queryset(query, user):
    queryset = generic_annotate(Content.objects.filter(query),
        Vote, Sum('votes__vote')).order_by("-score")
    scores = Vote.objects.get_scores_in_bulk(queryset)
    votes = Vote.objects.get_for_user_in_bulk(queryset, user)
    return {"queryset": queryset.select_subclasses(),
            "scores": scores, "votes": votes}


def get_search_results(qs, keyword, search_fields, nb_items=None):
    query_dict = get_queries_by_score(keyword, search_fields)
    keys = sorted(query_dict.keys(), reverse=True)
    results = list()
    for score in keys:
        query = query_dict.get(score)
        #TODO: better implementation, meaning find a way to use qs
        #   instead of lists
        item_list = list(qs.filter(query))
        for item in item_list:
            if not results.__contains__(item):
                results.append(item)
        if nb_items and len(results) >= nb_items:
            break
    results = results[:nb_items] if nb_items else results
    return results


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
            raise RedisError("Redis Server '%s' URL is not valid." \
                                                    % settings.REDISTOGO_URL)
        else:
            return None


@receiver(user_logged_in)
def update_redis_db(sender, request, user, **kwargs):
    engine = load_redis_engine()

    if not engine:
        return
    for key, value in PARAMS.iteritems():
        cls = value["class"]
        ctype = ContentType.objects.get_for_model(cls)
        for obj in cls.objects.all():
            record_object(engine, obj, key, value, ctype)


@receiver(post_save)
def redis_post_save(sender, instance=None, raw=False, **kwargs):
    key = "%s.%s" % (instance.__module__, instance._meta.object_name)
    if not key in PARAMS:
        return
    engine = load_redis_engine()
    if not engine:
        return
    value = PARAMS.get(key)

    record_object(engine, instance, key, value)


def record_object(engine, obj, key, value, ctype=None):
    if ctype is None:
        ctype = ContentType.objects.get_for_model(obj)
    obj_id = obj.__getattribute__(value["pk"])
    title = obj.__getattribute__(value["title_field"])
    if not title:
        return
    title = unicodedata.normalize('NFKD', title).encode('utf-8',
                                                        'ignore')
    data = {"class": key, "title": title}
    for field in value["recorded_fields"]:
        data.update({field: unicode(obj.__getattribute__(field))})
    engine.store_json(obj_id, title, data, ctype.id)


@receiver(post_delete)
def redis_post_delete(sender, instance=None, **kwargs):
    key = "%s.%s" % (instance.__module__, instance._meta.object_name)
    if not key in PARAMS:
        return
    engine = load_redis_engine()
    if not engine:
        return
    value = PARAMS[key]

    obj_id = instance.__getattribute__(value["pk"])
    ctype = ContentType.objects.get_for_model(instance)
    engine.remove(obj_id, ctype.id)
