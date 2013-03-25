from celery import task, current_task

@task()
def add(x, y):
    request = current_task.request
    print('Executing task id %r, args: %r kwargs: %r' % (
        request.id, request.args, request.kwargs))
    return x+y
