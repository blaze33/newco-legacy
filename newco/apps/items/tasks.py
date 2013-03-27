from celery import Celery
from django.conf import settings
celery = Celery('tasks', broker=settings.BROKER_URL)


@celery.task()
def update_cache(object):
    object.update_cache()
    return True
