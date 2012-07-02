from django.http import HttpResponseRedirect, HttpResponseServerError
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context

from follow.utils import toggle

from utils.tools import load_object


def process_following(request):
    obj = load_object(request)
    follow = toggle(request.user, obj)

    try:
        # Might be something better to do
        # than follow.target.get_absolute_url()
        return HttpResponseRedirect(follow.target.get_absolute_url())
    except (AttributeError, TypeError):
        if 'HTTP_REFERER' in request.META:
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
        elif follow:
            return HttpResponseServerError(
                        '"%s" object of type ``%s`` has no method ' + \
                        '``get_absolute_url()``.' % \
                        (unicode(follow.target), follow.target.__class__)
            )
        else:
            return HttpResponseServerError(
                        'No follow object and `next` parameter found.'
            )


def mail_followee(fwee, fwer, site):
    message_subject = "%s, %s vous suit maintenant sur NewCo !" % \
                            (fwee.name, fwer.name)

    txt_template = get_template('follow/_follow_notification_email.txt')
    html_template = get_template('follow/_follow_notification_email.html')

    d = Context({'followee': fwee.name, 'follower': fwer.name,
        'followee_url': "http://%s%s" % (site, fwee.get_absolute_url()),
        'follower_url': "http://%s%s" % (site, fwer.get_absolute_url()),
        'message_subject': message_subject
    })

    msg_txt = txt_template.render(d)
    msg_html = html_template.render(d)

    msg = EmailMultiAlternatives(message_subject, msg_txt,
        'auto-mailer@newco-project.fr', [fwee.user.email]
    )
    msg.attach_alternative(msg_html, "text/html")
    msg.send()
