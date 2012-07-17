from django import shortcuts

from items.models import Item
from taggit.models import Tag


def autocomplete(request, template_name="autocomplete/autocomplete.html",
                                                        extra_context=None):
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

    return shortcuts.render(request, template_name, context)
