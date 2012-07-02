from django.http import HttpResponseRedirect, HttpResponseServerError

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
