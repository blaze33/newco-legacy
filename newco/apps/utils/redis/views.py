import json

from django.http import HttpResponse
from django.views.generic import View

from django.contrib.contenttypes.models import ContentType

from taggit.models import Tag

from items.models import Item
from profiles.models import Profile
from utils.redis.tools import engine
from utils.tools import get_class_name, get_class_from_string

CLASS_MAP = {
    "item": get_class_name(Item),
    "profile": get_class_name(Profile),
    "tag": get_class_name(Tag)
}


class RedisView(View):

    def get(self, request, *args, **kwargs):
        if not engine:
            return HttpResponse(json.dumps([]))
        phrase = request.GET.get("q", "")
        limit = int(request.GET.get("limit", -1))

        filter_dict = request.GET.copy()
        if "class" in kwargs:
            filter_dict.update({"class": CLASS_MAP.get(kwargs["class"])})
        ids = filter_dict.getlist("id", [])
        classes = filter_dict.getlist("class")

        data = []
        if phrase:
            filters = []
            filtered_fields = ["class"]
            for field in filtered_fields:
                if field in filter_dict:
                    filtered_values = filter_dict.getlist(field)
                    filters.append(lambda i: i[field] in filtered_values)

            data = engine.search_json(phrase, limit=limit, filters=filters)
        elif not phrase and ids and len(classes) == 1:
            cls = get_class_from_string(classes[0])
            ctype = ContentType.objects.get_for_model(cls)
            for i in ids:
                obj_id = engine.kcombine(i, ctype.id)
                raw_data = engine.client.hget(engine.data_key, obj_id)
                if not raw_data:
                    continue
                data.append(json.loads(raw_data))

        return HttpResponse(json.dumps(data), mimetype='application/json')
