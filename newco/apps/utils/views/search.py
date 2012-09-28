import json
import re

from django.core.urlresolvers import reverse
from django.db.models.loading import get_model
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic.base import RedirectView

from taggit.models import Tag

from items.models import Item
from profiles.models import Profile
from utils.tools import load_redis_engine


class TypeaheadSearchView(RedirectView):

    def post(self, request, *args, **kwargs):
        if "typeahead_search" in request.POST:
            search = request.POST.get("typeahead_search")
            obj_class = request.POST.get("obj_class", "")
            obj_id = request.POST.get("obj_id", "")
            if obj_class and obj_id:
                obj_model = get_model(*re.split(".models.", obj_class))
                obj = obj_model.objects.get(id=obj_id)

                if obj_model == Item or obj_model == Profile:
                    response = obj.get_absolute_url()
                elif obj_model == Tag:
                    response = reverse("tagged_items", args=[obj.slug])
            else:
                response = "%s?q=%s" % (reverse("content_search"), search)
            return HttpResponseRedirect(response)
        return super(TypeaheadSearchView, self).post(request, *args, **kwargs)


def redis_to_json(request):

    engine = load_redis_engine()
    if not "q" in request.GET or not engine:
        return HttpResponse(list())
    q = request.GET.get("q")
    data = json.dumps(engine.search_json(q))

    return HttpResponse(data, mimetype='application/json')
