from django.http import HttpResponseRedirect, HttpResponseServerError
from django.db.models.loading import get_model

from follow.utils import toggle


def process_following(request):
    app_label = request.POST['app_label']
    object_name = request.POST['object_name']
    pk = request.POST['pk']
    model = get_model(app_label, object_name)
    obj = model._default_manager.get(pk=pk)
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
