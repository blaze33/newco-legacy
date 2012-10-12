from django.conf import settings

from utils.multitemplate.tools import (get_similar_templates,
                                       get_template_titles)


class MultiTemplateMixin(object):

    def get_context_data(self, **kwargs):
        if settings.DEBUG:
            templates = get_template_titles(self.get_template_names())
            kwargs.update({"templates": templates})
        return super(MultiTemplateMixin, self).get_context_data(**kwargs)

    def get_template_names(self):
        names = super(MultiTemplateMixin, self).get_template_names()
        names = get_similar_templates(names[0]) if settings.DEBUG else names
        return names

    def render_to_response(self, context, **response_kwargs):
        names = self.get_template_names()
        if settings.DEBUG:
            if "template" in self.request.GET:
                names = [self.request.GET.get("template")]
            context.update({"template": names[0]})
        return self.response_class(
            request=self.request,
            template=names,
            context=context,
            **response_kwargs
        )
