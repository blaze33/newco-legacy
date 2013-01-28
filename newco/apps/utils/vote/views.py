from django.http import HttpResponse, HttpResponseRedirect
from django.utils.decorators import method_decorator

from django.contrib.auth.decorators import permission_required

from voting.models import Vote

from items.models import Content, Question, Answer
from utils.messages import display_message, get_message
from utils.tools import load_object

VOTE_DIRECTIONS = (("up", 1), ("down", -1), ("clear", 0))


class VoteMixin(object):

    def post(self, request, *args, **kwargs):
        if "vote_button" in request.POST:
            obj = load_object(request)
            self.success_url = getattr(self, "success_url", None)
            if not self.success_url:
                self.success_url = obj.get_absolute_url()
            return self.process_voting(request, obj, self.success_url)
        else:
            return super(VoteMixin, self).post(request, *args, **kwargs)

    @method_decorator(permission_required("profiles.can_vote",
                                          raise_exception=True))
    def process_voting(self, request, obj, success_url):
        direction = request.POST['vote_button']
        kwargs = {}
        if obj.author != request.user:
            vote = dict(VOTE_DIRECTIONS)[direction]
            Vote.objects.record_vote(obj.select_parent(), request.user, vote)
            if obj.__class__ is Content:
                obj = obj.select_subclass()
            if obj.__class__ is Question:
                obj.sort_related_answers()
            elif obj.__class__ is Answer:
                obj.question.sort_related_answers()

            kwargs.update({"object": obj})
            key = "vote-{0}".format(direction)
            display_message(key, request, **kwargs)
        else:
            display_message("vote-warning", request, **kwargs)
        return HttpResponseRedirect(success_url)
