#!/bin/sh

# opentelemetry-bootstrap -a install

python manage.py collectstatic --noinput
python manage.py migrate
# python manage.py djstripe_sync_models

python manage.py qcluster &

DJANGO_SETTINGS_MODULE=builtwithdjango.settings
OTEL_RESOURCE_ATTRIBUTES=service.name=builtwithdjango
OTEL_EXPORTER_OTLP_ENDPOINT="$SIGNOZ_OTEL_COLLECTOR"

# opentelemetry-instrument \
#   --traces_exporter otlp_proto_http \
#   --metrics_exporter otlp_proto_http \

gunicorn -c gunicorn.config.py --bind 0.0.0.0:80 --workers 3 --threads 2 builtwithdjango.wsgi:application
