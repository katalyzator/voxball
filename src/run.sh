#!/bin/bash

trap "exit" INT

pip install -r /app/requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate --noinput
python manage.py index_mapping

if [[ $DEV == 1 ]]; then
    /app/manage.py runserver 0.0.0.0:8000
else
    WORKERS_COUNT=5
    if [[ $WORKNET == 'dev' ]]; then
        WORKERS_COUNT=2
    fi
    uwsgi --workers $WORKERS_COUNT --ini /app/uwsgi.ini
fi

# gunicorn --bind 0.0.0.0:8001 --workers 7 --timeout 120 --worker-class gevent --log-level=INFO --access-logfile - --error-logfile - --user 0 --group 0 votem.wsgi 
