import itertools
import re

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q, Sum
from django.db.models.loading import get_model
from django.utils.datastructures import SortedDict

from generic_aggregation import generic_annotate
from voting.models import Vote


def load_object(request):
    """
    Loads object from hidden fields in post request
    """
    app_label = request.POST["app_label"]
    object_name = request.POST["object_name"]
    object_id = request.POST["id"]
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

    return [normspace(' ',
                      (t[0] or t[1]).strip()) for t in findterms(query_string)]


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
    query_dict = SortedDict()
    for score in range(len(terms), 0, -1):
        queries = None
        term_combinations = itertools.combinations(terms, score)
        for term_combination in term_combinations:
            query = get_query("", search_fields, term_combination)
            queries = queries | (query) if queries is not None else (query)
        query_dict.update({score: queries})
    return query_dict


def get_search_results(qs, keyword, search_fields, nb_items=None):
    query_dict = get_queries_by_score(keyword, search_fields)
    results = list()
    for score, query in query_dict.items():
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


def get_sorted_queryset(queryset, user):
    queryset = generic_annotate(
        queryset, Vote, Sum('votes__vote')).order_by("-score")
    scores = Vote.objects.get_scores_in_bulk(queryset)
    votes = Vote.objects.get_for_user_in_bulk(queryset, user)
    return {"queryset": queryset.select_subclasses(),
            "scores": scores, "votes": votes}
