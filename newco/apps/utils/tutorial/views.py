
class TutoMixin(object):

    def get(self, request, *args, **kwargs):
        if request.session.get('visited', False):
            self.visited = True
        else:
            request.session['visited'] = True
            self.visited = False
        return super(TutoMixin, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        if self.visited:
            kwargs.update({"visited": True})
        else:
            kwargs.update({"visited": False})
        ctx = super(TutoMixin, self).get_context_data(**kwargs)
        return ctx
