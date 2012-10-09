import glob

from django.conf import settings
from utils.tools import get_template_source


class TrialTemplateMixin(object):

    def get_context_data(self, **kwargs):
        context = super(TrialTemplateMixin, self).get_context_data(**kwargs)
        if settings.DEBUG:
            names = super(TrialTemplateMixin, self).get_template_names()
            temp_src = get_template_source(names[0])
            prefix_length = len(temp_src)-5 # arrive before the ".html"

            template_matches = glob.glob(temp_src[0:prefix_length] + "*")

            temp_list = []
            for temp in template_matches:
                display_name = temp[prefix_length:len(temp)-5]
                temp_list.append(display_name)
            context.update({"trial_temp": temp_list})

        return context

    def get_template_names(self):
        names = super(TrialTemplateMixin, self).get_template_names()

        if "trial_template" in self.request.GET:
            # cut the ".html" and insert the suffix
            names[0] = names[0][0:len(names[0])-5] + self.request.GET['trial_template'] + ".html"

        return names
