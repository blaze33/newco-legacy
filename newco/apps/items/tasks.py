from celery import task, current_task

@task()
def update_cache(object):
    request = current_task.request
    print('Executing task id %r, args: %r kwargs: %r' % (
        request.id, request.args, request.kwargs))
    object.update_cache()
    return True
