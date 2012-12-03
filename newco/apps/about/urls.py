from django.conf.urls import patterns, include, url
from django.views.generic.simple import direct_to_template

KWARGS = {
    "faq": {"template": "about/faq.html"},
    "team": {"template": "about/team.html"},
    "contribute": {"template": "about/contribute.html"},
}

urlpatterns = patterns("",
    url(r"^faq/$", direct_to_template, KWARGS["faq"], name="faq"),
    url(r"^team/$", direct_to_template, KWARGS["team"], name="team"),
    url(r"^contribute/$", direct_to_template, KWARGS["contribute"],
        name="contribute"),
)
