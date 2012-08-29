from django.core.exceptions import ObjectDoesNotExist
from django.db.models.loading import get_model


def load_object(request):
    app_label = request.POST['app_label']
    object_name = request.POST['object_name']
    object_id = request.POST['id']
    model = get_model(app_label, object_name)

    lookup_kwargs = {'%s__exact' % model._meta.pk.name: object_id}

    try:
        return model._default_manager.get(**lookup_kwargs)
    except ObjectDoesNotExist:
        raise AttributeError('No %s for %s.' % (model._meta.app_label,
                                                lookup_kwargs))
