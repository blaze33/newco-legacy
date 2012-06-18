web: newrelic-admin run-program django-admin.py run_gunicorn -b 0.0.0.0:$PORT -k gevent -w 3 --max-requests 500 --preload --settings=$DJANGO_SETTINGS_MODULE
