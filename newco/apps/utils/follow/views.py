import json

from django.http import HttpResponse, HttpResponseRedirect
from django.utils.decorators import method_decorator

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from account.utils import user_display
from follow.utils import follow, unfollow
from utils.follow import Follow

from utils.mailtools import mail_followee
from utils.messages import add_message, render_messages
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
        user = request.user
        kwargs = {}
        if not user == obj:
            is_following = Follow.objects.is_following(user, obj)
            follow_obj = unfollow(user, obj) if is_following else \
                follow(user, obj)
            is_following = not is_following

            if follow_obj.target.__class__ is User:
                if is_following:
                    mail_followee(request, follow_obj.target, user)
                title = user_display(follow_obj.target)
            else:
                title = unicode(follow_obj.target)

            key = "follow" if is_following else "unfollow"
            kwargs.update({"object": title})
        else:
            key = "follow-warning"
        add_message(key, request, **kwargs)

        if request.is_ajax():
            messages = render_messages(request)
            data = {"is_following": is_following, "messages": messages}
            return HttpResponse(json.dumps(data), mimetype="application/json")
        else:
            return HttpResponseRedirect(success_url)
