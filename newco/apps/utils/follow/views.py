from django.utils.decorators import method_decorator

from django.contrib.auth.decorators import login_required

from utils.follow.tools import process_following as _process_following
from utils.tools import load_object


class ProcessFollowView(object):

    def post(self, request, *args, **kwargs):
        if "follow" in request.POST or "unfollow" in request.POST:
            obj = load_object(request)
            success_url = obj.get_absolute_url()
            return self.process_following(request, obj, success_url)
        else:
            return super(ProcessFollowView, self).post(request, *args,
                                                                **kwargs)

    @method_decorator(login_required)
    def process_following(self, request, obj, success_url):
        return _process_following(request, obj, success_url)
