#!/bin/bash
set -e

# web server
newrelic-admin run-program django-admin.py run_gunicorn \
-b 0.0.0.0:$PORT \
-k gevent \
-w $GUNICORN_WORKERS \
--max-requests $GUNICORN_MAX_REQUESTS \
--preload \
--settings=$DJANGO_SETTINGS_MODULE \
&

# celery default config
if [ -z $CELERY_WORKERS ]; then CELERY_WORKERS=2; fi
if [ -z $CELERY_CONCURRENCY ]; then CELERY_CONCURRENCY=100; fi
# celery asynchronous tasks
newrelic-admin run-program django-admin.py celeryd_multi \
start $CELERY_WORKERS \
-E \
-P gevent \
-c $CELERY_CONCURRENCY \
--loglevel=info \
&
django-admin.py celerycam &
# ensure all celery daemons exit
trap 'pkill -SIGTERM -f celeryd' INT TERM EXIT

# keep the process alive for foreman
wait
