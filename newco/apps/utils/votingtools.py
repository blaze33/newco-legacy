from django.http import HttpResponseRedirect, HttpResponseServerError

from voting.models import Vote

from utils.tools import load_object

VOTE_DIRECTIONS = (('up', 1), ('down', -1), ('clear', 0))


def process_voting(request, go_to_object=False):
    obj = load_object(request)
    direction = request.POST['vote_button']

    if obj.author != request.user:
        try:
            vote = dict(VOTE_DIRECTIONS)[direction]
        except KeyError:
            raise AttributeError(
                "'%s' is not a valid vote type." % direction
            )

        Vote.objects.record_vote(obj, request.user, vote)
    else:
        # TODO display message
        pass

    try:
        if go_to_object:
            return HttpResponseRedirect(obj.get_absolute_url())
        else:
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    except (AttributeError, TypeError):
        if 'HTTP_REFERER' in request.META:
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
        elif obj:
            return HttpResponseServerError(
                        '"%s" object of type ``%s`` has no method ' + \
                        '``get_absolute_url()``.' % \
                        (unicode(obj), obj.__class__)
            )
        else:
            return HttpResponseServerError(
                        'No follow object and `next` parameter found.'
            )