from django import template
from django.template import Context
from django.template.loader import get_template

register = template.Library()


@register.filter
def as_bootstrap_question_form(form):
    template = get_template("form/question_form.html")
    c = Context({"form": form})
    return template.render(c)
