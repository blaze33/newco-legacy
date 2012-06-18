web: newrelic-admin run-program django-admin.py run_gunicorn -b 0.0.0.0:$PORT -k gevent -w $GUNICORN_WORKERS --max-requests $GUNICORN_MAX_REQUESTS --preload --settings=$DJANGO_SETTINGS_MODULE
