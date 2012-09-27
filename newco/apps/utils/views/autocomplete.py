import json

from django.http import HttpResponse
from django.shortcuts import render

from taggit.models import Tag

from items.models import Item
from utils.tools import load_redis_engine


def autocomplete(request, template_name="autocomplete/autocomplete.html"):
    q = request.GET['q']  # crash if q is not in the url
    context = {'q': q}
    queries = {}
    queries['items'] = Item.objects.filter(
        name__icontains=q).distinct()[:4]
    queries['tags'] = Tag.objects.filter(
        name__icontains=q).distinct()[:2]

    # install queries into the context
    context.update(queries)

    # mix options
    options = 0
    for query in queries.values():
        options += len(query)
    context['options'] = options

    return render(request, template_name, context)


def redis_to_json(request):

    engine = load_redis_engine()
    if not "q" in request.GET or not engine:
        return HttpResponse(dict())
    q = request.GET.get("q")
    data = json.dumps(engine.search_json(q))

    return HttpResponse(data, mimetype='application/json')
