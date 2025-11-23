#!/bin/bash
source env/bin/activate
gunicorn core.wsgi:application --bind 0.0.0.0:$PORT
