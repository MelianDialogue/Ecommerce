#!/bin/bash
python manage.py migrate --noinput
python manage.py collectstatic --noinput
gunicorn ecommerceProject.wsgi:application --bind 0.0.0.0:$PORT
