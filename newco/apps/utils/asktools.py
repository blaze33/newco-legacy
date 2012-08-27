from django.http import HttpResponseRedirect
from django.core.mail import EmailMultiAlternatives
from django.core.urlresolvers import reverse
from django.template.loader import get_template
from django.template import Context
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext
from account.utils import user_display


def process_asking(request, question, success_url, item=None):
    msgs = {
        "ask": {
            "level": messages.INFO,
            "text": _(
                "%(user)s, your request has been sent to %(ask_profile)s!"
            )
        },
        "warning": {
            "level": messages.WARNING,
            "text": _("%(user)s, you can't ask yourself to answer a question!")
        },
    }

    user_profile = request.user.get_profile()
    username = user_display(request.user)
    site = request.META.get('HTTP_HOST')

    if "ask" in request.POST:
        requested_user = User.objects.get(id=request.POST["ask"])
        requested_profile = requested_user.get_profile()

    #TODO: improve typeahead
#    elif "ask_prof_pick" in request.POST:
#        ask_profile_search = request.POST["ask_prof_pick"]
#        profile_list = Profile.objects.filter(name=ask_profile_search)
#        if profile_list.count() > 0:
#            profile = profile_list[0]
#        else:
#            pass

    if requested_user != request.user or True:
        mail_askee(requested_profile, user_profile, site, question, item)
        messages.add_message(request, msgs["ask"]["level"],
            msgs["ask"]["text"] % {
                "user": username, "ask_profile": requested_profile
            }
        )
    else:
        messages.add_message(request, msgs["warning"]["level"],
            msgs["warning"]["text"] % {"user": username}
        )
        if item:
            success_url = item.get_absolute_url()

    return HttpResponseRedirect(success_url)


def mail_askee(askee, asker, site, question, item):
    #TODO: add links to question and item

    message_subject = _("%(askee)s, %(asker)s needs you help!") % \
                            {"askee": askee.name, "asker": asker.name}

    txt_template = get_template("ask/_ask_notification_email.txt")
    html_template = get_template("ask/_ask_notification_email.html")

    txt_req = _('would like you to answer this question "%(question)s"') % \
                                                {"question": question.content}
    if item:
        txt_req = txt_req + " " + _("about the product %(product)s.") % \
                                                        {"product": item.name}
    else:
        items = question.items.select_related()
        nb_items = items.count()
        if nb_items == 1:
            txt_req = txt_req + " " + _("about the product %(product)s.") % \
                                                    {"product": items[0].name}
        elif nb_items > 1:
            print nb_items
            txt_req = txt_req + " " + ugettext("on")
            for i, item in enumerate(items):
                print i
                txt_req = txt_req + " " + item.name
                if i < 4 and i != (nb_items - 1):
                    txt_req = txt_req + ","
                elif i == 4:
                    if nb_items > 4:
                        txt_req = txt_req + "..."
                    break

    d = Context({"askee": askee.name, "asker": asker.name,
        "askee_url": "http://%s%s" % (site, askee.get_absolute_url()),
        "asker_url": "http://%s%s" % (site, asker.get_absolute_url()),
        "message_subject": message_subject,
        "txt_request": txt_req,
        "settings_url": reverse("account_settings")
    })

    msg_txt = txt_template.render(d)
    msg_html = html_template.render(d)

    msg = EmailMultiAlternatives(message_subject, msg_txt,
        "auto-mailer@newco-project.fr", [askee.user.email]
    )
    msg.attach_alternative(msg_html, "text/html")
    msg.send()
