from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.template import Context
from django.template.loader import get_template
from django.utils.translation import ugettext
from django.utils.translation import ugettext_lazy as _

from django.contrib import messages
from django.contrib.auth.models import User

from account.utils import user_display

#from utils.models import LastMail


def send_mail(message_subject, receiver, txt_template, html_template, context):
    msg_txt = txt_template.render(context)
    msg_html = html_template.render(context)

    msg = EmailMultiAlternatives(message_subject, msg_txt,
        '"NewCo" <notifications@newco-project.fr>', [receiver.email]
    )
    msg.attach_alternative(msg_html, "text/html")

#    waiting_time = datetime.timedelta(minutes=1)
#    last_mail, created = LastMail.objects.get_or_create(user=receiver)
#    diff = timezone.now() - last_mail.modified
#    if diff > waiting_time or created:
#        last_mail.save()
    #if not settings.DEBUG:
    msg.send()


def mail_question_author(site, answer):

    question = answer.question
    receiver = question.author
    receiver_name = user_display(receiver)
    receiver_url = "http://%s%s" % (site, receiver.get_absolute_url())
    answerer = answer.author
    answerer_name = user_display(answerer)
    answerer_url = "http://%s%s" % (site, answerer.get_absolute_url())

    msg_subject = _("%s, %s has answered your question!") % \
                            (receiver_name, answerer_name)

    txt_template = get_template("mail/_answer_notification_email.txt")
    html_template = get_template("mail/_answer_notification_email.html")

    title_txt = _('<a href="%(receiver_url)s">%(receiver)s</a>,<br>'
        '<a href="%(answerer_url)s">%(answerer)s</a> has answered your '
        'question about the '
        ) % \
        {"receiver_url": receiver_url,
        "receiver": receiver_name,
        "answerer_url": answerer_url,
        "answerer": answerer_name,
        }

    items = question.items.select_related()
    nb_items = items.count()
    if nb_items >= 1:
        if nb_items == 1:
            title_txt += unicode(_('product '))
        else:
            title_txt += unicode(_('products '))

        for i, item in enumerate(items):
            title_txt += _('<a href="%(product_url)s">%(product)s</a>') % \
                {"product_url": "http://%s%s" % (site, item.get_absolute_url()),
                "product": item.name,}
            if i < (nb_items - 2):
                title_txt += unicode(_(", "))
            elif i == (nb_items - 2):
                title_txt += unicode(_(" and "))
        title_txt += unicode(_(":")) # _(":")

    elif nb_items == 0:
        tags = question.tags
        nb_tags = tags.all().count()
        if nb_tags == 1:
            title_txt += unicode(_("tag "))
        else:
            title_txt += unicode(_("tags "))
        for i, tag in enumerate(tags.all()):
            title_txt += _('<a href="%(tag_url)s">%(tag)s</a>') % \
                {"tag_url": "http://%s%s" % \
                    (site, reverse("tagged_items", args=[tag.slug])),
                "tag": tag.name,
                }
            if i < (nb_tags - 2):
                title_txt += unicode(_(", "))
            elif i == (nb_tags - 2):
                title_txt += unicode(_(" and "))

        title_txt += unicode(_(":"))

    context = Context({
        "title_txt": title_txt,
        "answer": answer,
    })

    send_mail(msg_subject, receiver, txt_template, html_template, context)


def process_asking_for_help(request, question, success_url, item=None):
    msgs = {
        "ask": {
            "level": messages.INFO,
            "text": _(
                "%(user)s, your request has been sent to %(receiver)s!"
            )
        },
        "warning": {
            "level": messages.WARNING,
            "text": _("%(user)s, you can't ask yourself to answer a question!")
        },
    }

    username = user_display(request.user)
    site = request.META.get('HTTP_HOST')

    if "ask" in request.POST:
        receiver = User.objects.get(id=request.POST["ask"])
        receiver_name = user_display(receiver)

    #TODO: improve typeahead
#    elif "ask_prof_pick" in request.POST:
#        ask_profile_search = request.POST["ask_prof_pick"]
#        profile_list = Profile.objects.filter(name=ask_profile_search)
#        if profile_list.count() > 0:
#            profile = profile_list[0]
#        else:
#            pass

        if receiver != request.user:
            mail_helper(receiver, request.user, site, question, item)
            messages.add_message(request, msgs["ask"]["level"],
                msgs["ask"]["text"] % {
                    "user": username, "receiver": receiver_name
                }
            )
        else:
            messages.add_message(request, msgs["warning"]["level"],
                msgs["warning"]["text"] % {"user": username}
            )

    return HttpResponseRedirect(success_url)


def mail_helper(receiver, requester, site, question, item):
    #TODO: add links to question and item

    receiver_name = user_display(receiver)
    requester_name = user_display(requester)

    msg_subject = _("%(receiver)s, %(requester)s needs your help!") % \
                    {"receiver": receiver_name, "requester": requester_name}

    txt_template = get_template("mail/_ask_notification_email.txt")
    html_template = get_template("mail/_ask_notification_email.html")

    txt_req = _('would like you to answer this question "%(question)s"') % \
                                                {"question": question.content}
    if item:
        txt_req = txt_req + " " + _("about the product %(product)s.") % \
                                                        {"product": item.name}
    else:
        items = question.items.select_related()
        nb_items = items.count()
        if nb_items == 1:
            item = items[0]
            txt_req = txt_req + " " + _("about the product %(product)s.") % \
                                                    {"product": item.name}
        elif nb_items > 1:
            item = items[0]
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

    context = Context({"receiver": receiver_name, "requester": requester_name,
        "askee_url": "http://%s%s" % (site, receiver.get_absolute_url()),
        "asker_url": "http://%s%s" % (site, requester.get_absolute_url()),
        "message_subject": msg_subject,
        "question_object": unicode(question),
        "product_object": item.name,
        "question_url": "http://%s%s" % (site, question.get_absolute_url()),
        "product_url": "http://%s%s" % (site, item.get_absolute_url()),
        "txt_request": txt_req,
        "settings_url": "http://%s%s" % (site, reverse("account_settings"))
    })

    send_mail(msg_subject, receiver, txt_template, html_template, context)
