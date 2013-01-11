from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.views.generic.base import RedirectView

from taggit.models import Tag

from items.models import Item
from profiles.models import Profile
from utils.tools import get_class_from_string


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
                # TODO: handle no results
                response = "/"
            return HttpResponseRedirect(response)
        return super(TypeaheadSearchView, self).post(request, *args, **kwargs)
