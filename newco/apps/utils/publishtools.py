from django.contrib import messages
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _


from utils.tools import load_object
from account.utils import user_display


def process_publishing(self, request):
    
    obj = load_object(request)
    
    msgs = {
        "published": {
            "level": messages.SUCCESS,
            "text": _("Your %(object)s has been published, %(user)s" % {"object" : obj._meta.module_name, "user" : user_display(request.user)})
        },
        "draft": {
            "level": messages.WARNING,
            "text": _("Your %(object)s has been un-published to draft, %(user)s" % {"object" : obj._meta.module_name, "user" : user_display(request.user)})
        },
        "unknown": {
            "level": messages.ERROR,
            "text": _("Your request hasn't been recognized. It may be a bug, your %(object)s has not changed status." % {"object" : obj._meta.module_name})
        },
    }

    if self.request.POST['status'] == "published":
        obj.status = obj.STATUS.published
        messages.add_message(request, msgs["published"]["level"],
                             msgs["published"]["text"]
        )
        obj.save()
    elif self.request.POST['status'] == "draft":
        obj.status = obj.STATUS.draft
        messages.add_message(request, msgs["draft"]["level"],
             msgs["draft"]["text"]
        )
        obj.save()
    else:
        messages.add_message(request, msgs["unknown"]["level"],
             msgs["unknown"]["text"]
        )
    
    return HttpResponseRedirect('')
