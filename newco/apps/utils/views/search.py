import json

from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import View
from django.views.generic.base import RedirectView

from taggit.models import Tag

from items.models import Item
from profiles.models import Profile
from utils.tools import get_class_from_string
from utils.redistools import load_redis_engine


class TypeaheadSearchView(RedirectView):

    def post(self, request, *args, **kwargs):
        if "q" in request.POST:
            q = request.POST.get("q")
            obj_class = request.POST.get("obj_class", "")
            obj_id = request.POST.get("obj_id", "")
            cls = get_class_from_string(obj_class)
            if cls and obj_id:
                obj = cls.objects.get(id=obj_id)

                if cls is Item or cls is Profile:
                    response = obj.get_absolute_url()
                elif cls is Tag:
                    response = reverse("tagged_items", args=[obj.slug])
            else:
                response = "%s?q=%s" % (reverse("content_search"), q)
            return HttpResponseRedirect(response)
        return super(TypeaheadSearchView, self).post(request, *args, **kwargs)


class RedisView(View):

    def get(self, request, *args, **kwargs):
        engine = load_redis_engine()
        if not "q" in request.GET or not engine:
            return HttpResponse(json.dumps(list()))
        q = request.GET.get("q")
        limit = int(request.GET.get("limit", -1))

        filters = list()
        filtered_fields = ["class"]
        for field in filtered_fields:
            if field in request.GET:
                filtered_values = request.GET.getlist(field)
                filters.append(lambda i: i[field] in filtered_values)

        data = json.dumps(engine.search_json(q, limit=limit, filters=filters))

        return HttpResponse(data, mimetype='application/json')
