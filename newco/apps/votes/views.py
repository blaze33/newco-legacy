from django.http import HttpResponseRedirect
from django.db.models.loading import get_model
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist

from voting.views import vote_on_object

APP_NAME = 'items'


@login_required
def rate_object(request, model_name, object_id):

    model = get_model(APP_NAME, model_name)

    if 'vote_button' in request.POST:
        return vote_on_object(request, model, request.POST['vote_button'],
                object_id=object_id)
    else:
        lookup_kwargs = {}
        lookup_kwargs['%s__exact' % model._meta.pk.name] = object_id

        try:
            obj = model._default_manager.get(**lookup_kwargs)
        except ObjectDoesNotExist:
            raise AttributeError('No %s for %s.' % (model._meta.app_label,
                                                    lookup_kwargs))

        return HttpResponseRedirect(obj.get_absolute_url())
