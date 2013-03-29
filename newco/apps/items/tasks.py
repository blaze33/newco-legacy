from celery import Celery
from django.conf import settings
celery = Celery('tasks', backend=settings.CELERY_RESULT_BACKEND)


@celery.task()
def update_cache(object):
    object.update_cache()
    return True
