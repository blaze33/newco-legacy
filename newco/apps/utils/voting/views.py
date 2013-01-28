import json

from django.http import HttpResponse, HttpResponseRedirect
from django.utils.decorators import method_decorator

from django.contrib.auth.decorators import permission_required

from items.models import Content, Question, Answer
from utils.messages import display_message, get_message
from utils.tools import load_object
from utils.voting import Vote

VOTE_DIRECTIONS = (("up", 1), ("down", -1), ("clear", 0))
BUTTONS_CONF = {
    1: {"up": {"value": "clear", "dataVote": "True"},
        "down": {"value": "down", "dataVote": "False"}},
    0: {"up": {"value": "up", "dataVote": "False"},
        "down": {"value": "down", "dataVote": "False"}},
    -1: {"up": {"value": "up", "dataVote": "False"},
         "down": {"value": "clear", "dataVote": "True"}}
}


class VoteMixin(object):

    def post(self, request, *args, **kwargs):
        if "vote-up" in request.POST or "vote-down" in request.POST:
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
        direction = request.POST["vote-up"] if "vote-up" in request.POST else \
            request.POST["vote-down"]
        kwargs = {}
        if obj.author != request.user:
            vote = dict(VOTE_DIRECTIONS)[direction]
            content_obj = obj.select_parent()
            Vote.objects.record_vote(content_obj, request.user, vote)
            if obj.__class__ is Content:
                obj = obj.select_subclass()
            if obj.__class__ is Question:
                obj.sort_related_answers()
            elif obj.__class__ is Answer:
                obj.question.sort_related_answers()

            kwargs.update({"object": obj})
            key = "vote-{0}".format(direction)
            score = Vote.objects.get_score(content_obj)
            vote = Vote.objects.get_for_user(content_obj, request.user)
            conf = BUTTONS_CONF[vote.vote]
            data = {"conf": conf, "score": score, "ok": True}
        else:
            data = {"ok": False}
            key = "vote-warning"
        if request.is_ajax():
            message = get_message(key, request, **kwargs)
            data.update({"message": message})
            return HttpResponse(json.dumps(data), mimetype="application/json")
        else:
            display_message(key, request, **kwargs)
            return HttpResponseRedirect(success_url)
