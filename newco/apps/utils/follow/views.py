from django.utils.decorators import method_decorator

from django.contrib.auth.decorators import login_required

from utils.follow.tools import process_following as _process_following
from utils.tools import load_object


class FollowMixin(object):

    def post(self, request, *args, **kwargs):
        if "follow" in request.POST or "unfollow" in request.POST:
            self.object = load_object(request)
            return self.process_following(
                request, self.object, self.get_success_url())
        else:
            return super(FollowMixin, self).post(request, *args, **kwargs)

    @method_decorator(login_required)
    def process_following(self, request, obj, success_url):
        return _process_following(request, obj, success_url)

    def get_success_url(self):
        success_url = getattr(self, "success_url", None)
        if success_url:
            return success_url
        next = self.request.POST.get("next", None)
        return next if next else self.object.get_absolute_url()
