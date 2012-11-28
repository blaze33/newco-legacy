

class TutorialMixin(object):

    def get(self, request, *args, **kwargs):
        self.visited = request.session.get("visited", False)
        if not self.visited:
            request.session["visited"] = True
        return super(TutorialMixin, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        self.visited = getattr(self, "visited", True)
        if self.visited is False and not "welcome" in self.request.GET:
            kwargs.update({"launch_tutorial": True})
        return super(TutorialMixin, self).get_context_data(**kwargs)
