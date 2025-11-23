#!/bin/bash
source env/bin/activate
python manage.py collectstatic --noinput
python manage.py collectstatic --noinput
gunicorn core.wsgi:application --timeout 120 --workers 3
