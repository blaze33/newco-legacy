from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.template import Context
from django.template.loader import get_template
from django.utils.translation import ugettext_lazy as _
from django.utils import translation

from django.contrib import messages
from django.contrib.auth.models import User

from account.utils import user_display

#from utils.models import LastMail
from utils.templatetags.tools import get_content_source


def send_mail(msg_sub, receiver, txt_template, html_template, context, sender):
    # ToDo : make the subject of email translated in "send_mail", to factorize the translation in this function ? (only thing that make it not possible )
    # translation.activate(receiver.account.language)
    msg_txt = txt_template.render(context)
    msg_html = html_template.render(context)

    email = receiver.email if not settings.DEBUG else sender.email
    newco = '"NewCo" <notifications@newco-project.fr>'
    msg = EmailMultiAlternatives(msg_sub, msg_txt, newco, [email])
    msg.attach_alternative(msg_html, "text/html")

#    waiting_time = datetime.timedelta(minutes=1)
#    last_mail, created = LastMail.objects.get_or_create(user=receiver)
#    diff = timezone.now() - last_mail.modified
#    if diff > waiting_time or created:
#        last_mail.save()
    msg.send()
    # translation.deactivate()


def mail_question_author(request, answer):
    question = answer.question
    receiver = question.author
    receiver_name = user_display(question.author)
    answerer = answer.author
    answerer_name = user_display(answer.author)

    translation.activate(receiver.account.language)

    msg_subject = _("%(receiver)s, %(answerer)s has answered your question!") % \
                {"receiver": receiver_name, "answerer": answerer_name}

    txt_template = get_template("mail/_answer_notification_email.txt")
    html_template = get_template("mail/_answer_notification_email.html")

    context = Context({
        "answer": answer,
        "request": request,
        "receiver": receiver_name,
        "receiver_url": request.build_absolute_uri(receiver.get_absolute_url()),
        "answerer": answerer_name,
        "answerer_url": request.build_absolute_uri(answerer.get_absolute_url()),
        "message_subject": msg_subject,
    })
    send_mail(msg_subject, receiver, txt_template, html_template, context,
              answerer)
    translation.deactivate()


def process_asking_for_help(request, question, success_url):
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
            mail_helper(request, receiver, request.user, question)
            messages.add_message(
                request, msgs["ask"]["level"], msgs["ask"]["text"] % {
                    "user": username, "receiver": receiver_name}
            )
        else:
            messages.add_message(request, msgs["warning"]["level"],
                                 msgs["warning"]["text"] % {"user": username})

    return HttpResponseRedirect(success_url)


def mail_helper(request, receiver, requester, question):
    translation.activate(receiver.account.language)

    receiver_name = user_display(receiver)
    requester_name = user_display(requester)

    msg_subject = _("%(receiver)s, %(requester)s needs your help!") % \
                    {"receiver": receiver_name, "requester": requester_name}

    txt_template = get_template("mail/_ask_notification_email.txt")
    html_template = get_template("mail/_ask_notification_email.html")

    context = Context({
        "receiver": receiver_name,
        "receiver_url": request.build_absolute_uri(receiver.get_absolute_url()),
        "asker": requester_name,
        "asker_url": request.build_absolute_uri(requester.get_absolute_url()),
        "request": request,
        "message_subject": msg_subject,
        "question": question,
        "question_url": request.build_absolute_uri(
            question.get_absolute_url()),
        "settings_url": request.build_absolute_uri(reverse("account_settings"))
    })

    send_mail(msg_subject, receiver, txt_template, html_template, context,
              requester)
    translation.activate(requester.account.language)


def mail_followee(request, fwee, fwer):
    translation.activate(fwee.account.language)
    fwee_name = user_display(fwee)
    fwer_name = user_display(fwer)

    msg_subject = "%s, %s is now following you on NewCo!" % \
                  (fwee_name, fwer_name)

    txt_template = get_template("mail/_follow_notification_email.txt")
    html_template = get_template("mail/_follow_notification_email.html")

    context = Context({
        "followee": fwee,
        "follower": fwer,
        "followee_url": request.build_absolute_uri(fwee.get_absolute_url()),
        "follower_url": request.build_absolute_uri(fwer.get_absolute_url()),
        "request": request,
        "message_subject": msg_subject
    })

    send_mail(msg_subject, fwee, txt_template, html_template, context, fwer)
    translation.activate(fwer.account.language)
