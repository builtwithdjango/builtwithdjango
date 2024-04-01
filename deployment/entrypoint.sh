#!/bin/sh

python manage.py collectstatic --noinput
python manage.py migrate

# python manage.py djstripe_sync_models
# python manage.py qcluster &
