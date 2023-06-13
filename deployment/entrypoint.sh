#!/bin/sh

python manage.py collectstatic --noinput
python manage.py migrate
# python manage.py djstripe_sync_models

python manage.py qcluster &

gunicorn --bind 0.0.0.0:80 --workers 3 builtwithdjango.wsgi:application
