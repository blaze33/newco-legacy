
class TutoMixin(object):

    def get(self, request, *args, **kwargs):
        self.visited = request.session.get("visited", False)
        if not self.visited:
            request.session["visited"] = True
        return super(TutoMixin, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        kwargs.update({"visited": self.visited})
        return super(TutoMixin, self).get_context_data(**kwargs)
