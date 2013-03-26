from celery import Celery
celery = Celery('tasks')


@celery.task()
def update_cache(object):
    object.update_cache()
    return True
