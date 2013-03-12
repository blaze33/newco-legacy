from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView

urlpatterns = patterns("",
    url(r"^faq/$", TemplateView.as_view(template_name="about/faq.html"),
        name="faq"),
    url(r"^team/$", TemplateView.as_view(template_name="about/team.html"),
        name="team"),
    url(r"^contribute/$",
        TemplateView.as_view(template_name="about/contribute.html"),
        name="contribute"),
)
