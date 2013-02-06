import htmlentitydefs
import itertools
import re

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.utils.datastructures import SortedDict

MODULE_PATTERN = "(?P<module_name>[\w+\.?]+)\.(?P<fromlist>\w+)$"


def get_class_name(klass):
    return "{0}.{1}".format(klass.__module__, klass._meta.object_name)


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
    model = get_class_from_string(request.POST["class_name"])
    object_id = request.POST["id"]

    lookup_kwargs = {"{0}__exact".format(model._meta.pk.name): object_id}

    try:
        return model._default_manager.get(**lookup_kwargs)
    except ObjectDoesNotExist:
        raise AttributeError("No {0} for {1}.".format(model._meta.app_label,
                                                      lookup_kwargs))


def normalize_query(str, findterms=re.compile(r'"([^"]+)"|(\S+)').findall,
                    normspace=re.compile(r'\s{2,}').sub):
    """
    Splits the query string in invidual keywords, getting rid of unecessary
    spaces and grouping quoted words together.

    Example::

        >>> normalize_query(' some random  words "with quotes  " and   spaces')
        ['some', 'random', 'words', 'with quotes', 'and', 'spaces']
    """

    terms = [normspace(' ', (t[0] or t[1]).strip()) for t in findterms(str)]
    return uniquify_sequence(terms)


def get_query(query_string, search_fields, terms=None, min_len=1):
    """
    Returns a query, that is a combination of Q objects. That combination
    aims to search keywords within a model by testing the given search fields.
    """

    if not terms:
        kwargs = {"findterms": re.compile(
            r'"([^"]+)"|(\S{%d,})' % min_len).findall} if min_len > 1 else {}
        terms = normalize_query(query_string, **kwargs)
    query = None
    for term in terms:
        or_query = None
        for field_name in search_fields:
            q = Q(**{"%s__icontains" % field_name: term})
            or_query = q if or_query is None else or_query | q
        query = or_query if query is None else query & or_query
    return query


def get_queries_by_score(query_string, search_fields, min_len=1):
    """
    Returns a list of queries, with each element being a combination of
    Q objects. That combination aims to search keywords within a model
    by testing the given search fields.
    """

    kwargs = {"findterms": re.compile(
        r'"([^"]+)"|(\S{%d,})' % min_len).findall} if min_len > 1 else {}
    terms = normalize_query(query_string, **kwargs)
    query_dict = SortedDict()
    for score in range(len(terms), 0, -1):
        queries = None
        term_combinations = itertools.combinations(terms, score)
        for term_combination in term_combinations:
            query = get_query("", search_fields, term_combination)
            queries = queries | (query) if queries is not None else (query)
        query_dict.update({score: queries})
    return query_dict


def get_search_results(qs, keyword, search_fields, min_len, nb_items=None):
    query_dict = get_queries_by_score(keyword, search_fields, min_len)
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


def uniquify_sequence(seq):
    seen = set()
    seen_add = seen.add
    return [x for x in seq if x not in seen and not seen_add(x)]


def unescape(text):
    """
    Removes HTML or XML character references and entities from a text string.

    @param text The HTML (or XML) source text.
    @return The plain text, as a Unicode string, if necessary.
    """
    def fixup(m):
        text = m.group(0)
        if text[:2] == "&#":
            # character reference
            try:
                if text[:3] == "&#x":
                    return unichr(int(text[3:-1], 16))
                else:
                    return unichr(int(text[2:-1]))
            except ValueError:
                pass
        else:
            # named entity
            try:
                text = unichr(htmlentitydefs.name2codepoint[text[1:-1]])
            except KeyError:
                pass
        return text  # leave as is
    return re.sub("&#?\w+;", fixup, text)

def fill_product_list_by_tag(list_products_by_tag,nb_products,top_products,list_doublons_p):
        count = 0
        for product in top_products:
            if count == nb_products:
                break
            elif product not in list_doublons_p:
                list_products_by_tag.append(product)
                count += 1
        if list_products_by_tag:
            ##### Loop to add the N products to list_doublons_p ####
                for i in range(nb_products):
                    if len(list_products_by_tag)>i:
                        list_doublons_p.append(list_products_by_tag[i])

def fill_question_list_by_tag(list_questions_by_tag,nb_questions,top_questions,list_doublons_q,tag,top_question_by_tag):
        count = 0
        for question in top_questions:
            if count == nb_questions:
                break
            elif question not in list_doublons_q:
                list_questions_by_tag.append(question)
                count += 1  
        if list_questions_by_tag:
        ##### Loop to add the question to list_doublons_q ####
            for i in range(nb_questions):
                if len(list_questions_by_tag)>i:
                    list_doublons_q.append(list_questions_by_tag[i])
            top_question_by_tag[tag]=list_questions_by_tag[:nb_questions]
