#!/bin/bash
source env/bin/activate
export PORT=${PORT:-8000}
python manage.py collectstatic --noinput
gunicorn core.wsgi:application --bind 0.0.0.0:$PORT
