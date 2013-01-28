from django.utils.decorators import method_decorator

from django.contrib.auth.decorators import login_required

from utils.follow.tools import process_following as _process_following
from utils.tools import load_object


class FollowMixin(object):

    def post(self, request, *args, **kwargs):
        if "follow" not in request.POST:
            return super(FollowMixin, self).post(request, *args, **kwargs)

        obj = load_object(request)
        self.success_url = getattr(self, "success_url", None)
        if not self.success_url:
            next = self.request.POST.get("next", None)
            self.success_url = next if next else obj.get_absolute_url()
        return self.process_following(request, obj, self.get_success_url())

    @method_decorator(login_required)
    def process_following(self, request, obj, success_url):
        return _process_following(request, obj, success_url)
