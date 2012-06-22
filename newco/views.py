from django.http import HttpResponsePermanentRedirect
from django.http import HttpResponseRedirect, HttpResponseGone
from django.views.generic.base import RedirectView, TemplateView


class HomePageRedirectView(RedirectView, TemplateView):

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            url = request.user.get_profile().get_absolute_url()
            if url:
                if self.permanent:
                    return HttpResponsePermanentRedirect(url)
                else:
                    return HttpResponseRedirect(url)
            else:
                return HttpResponseGone()
        else:
            self.template_name = "homepage.html"
            context = self.get_context_data(**kwargs)
            return self.render_to_response(context)