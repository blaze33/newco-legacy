import itertools
import re

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q, Sum
from django.db.models.loading import get_model
from django.template.base import TemplateSyntaxError, kwarg_re
from django.utils.datastructures import SortedDict
from django.utils.encoding import smart_str

from generic_aggregation import generic_annotate
from voting.models import Vote

MODULE_PATTERN = "(?P<module_name>[\w+\.?]+)\.(?P<fromlist>\w+)$"


def get_class_name(klass):
    return "%s.%s" % (klass.__module__, klass._meta.object_name)


def get_class_from_string(class_string, pattern=MODULE_PATTERN):
    match_obj = re.match(pattern, class_string)
    if not match_obj:
        print "Class string expresion didn't match pattern '%s'" % pattern
        return None
    try:
        module = __import__(match_obj.group("module_name"),
                            fromlist=[match_obj.group("fromlist")])
    except ImportError:
        print "Failed to import module <%s>" % match_obj.group("module_name")
        return None

    cls = getattr(module, match_obj.group("fromlist"), None)
    if not cls:
        print "Module <%s> doesn't have class '%s'" % \
            (match_obj.group("module_name"), match_obj.group("fromlist"))
    return cls


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


def get_node_extra_arguments(parser, bits, tag_name, max_args):
    args = []
    kwargs = {}
    asvar = None
    if len(bits) >= 2 and bits[-2] == 'as':
        asvar = bits[-1]
        bits = bits[:-2]

    if len(bits):
        if len(bits) <= max_args:
            for bit in bits:
                match = kwarg_re.match(bit)
                if not match:
                    err_msg = "Malformed arguments in '%s'" % tag_name
                    raise TemplateSyntaxError(err_msg)
                name, val = match.groups()
                if name:
                    kwargs[name] = parser.compile_filter(val)
                else:
                    args.append(parser.compile_filter(val))
        else:
            err_msg = "'%s' tag takes at most %d extra arguments." \
                % (tag_name, max_args)
            raise TemplateSyntaxError(err_msg)

    return [args, kwargs, asvar]


def resolve_template_args(context, in_args, in_kwargs):
    args = [arg.resolve(context) for arg in in_args]
    kwargs = dict([(smart_str(k, 'ascii'), v.resolve(context))
                   for k, v in in_kwargs.items()])
    return [args, kwargs]
