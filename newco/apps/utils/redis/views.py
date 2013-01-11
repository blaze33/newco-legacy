import json

from django.http import HttpResponse
from django.views.generic import View

from taggit.models import Tag

from items.models import Item
from profiles.models import Profile
from utils.redis.tools import engine
from utils.tools import get_class_name

CLASS_MAP = {
    "item": get_class_name(Item),
    "profile": get_class_name(Profile),
    "tag": get_class_name(Tag)
}


class RedisView(View):

    def get(self, request, *args, **kwargs):
        if not "q" in request.GET or not engine:
            return HttpResponse(json.dumps(list()))
        q = request.GET.get("q")
        limit = int(request.GET.get("limit", -1))

        filter_dict = request.GET.copy()

        if "class" in kwargs:
            filter_dict.update({"class": CLASS_MAP.get(kwargs.get("class"))})
        filters = list()
        filtered_fields = ["class"]
        for field in filtered_fields:
            if field in filter_dict:
                filtered_values = filter_dict.getlist(field)
                filters.append(lambda i: i[field] in filtered_values)

        data = json.dumps(engine.search_json(q, limit=limit, filters=filters))

        return HttpResponse(data, mimetype='application/json')
