from django.utils.decorators import method_decorator

from django.contrib.auth.decorators import permission_required

from utils.vote.tools import process_voting as _process_voting
from utils.tools import load_object


class ProcessVoteView(object):

    def post(self, request, *args, **kwargs):
        if "vote_button" in request.POST:
            obj = load_object(request)
            if not self.success_url:
                self.success_url = obj.get_absolute_url()
            return self.process_voting(request, obj, self.success_url)
        else:
            return super(ProcessVoteView, self).post(request, *args,
                                                                **kwargs)

    @method_decorator(permission_required("profiles.can_vote",
                                          raise_exception=True))
    def process_voting(self, request, obj, success_url):
        return _process_voting(request, obj, success_url)
