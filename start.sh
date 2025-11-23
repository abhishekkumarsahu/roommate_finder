#!/usr/bin/env bash
gunicorn core.wsgi:application --bind 0.0.0.0:$PORT
