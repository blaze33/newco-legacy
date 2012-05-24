from django.http import Http404
from django.db.models.loading import get_model

from voting.views import vote_on_object

APP_NAME = 'items'


def rate_object(request, model_name, object_id):

    model = get_model(APP_NAME, model_name)

    if 'vote_button' in request.POST:
        return vote_on_object(request, model, request.POST['vote_button'],
                object_id=object_id)
    else:
        return Http404
