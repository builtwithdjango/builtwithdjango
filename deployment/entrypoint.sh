#!/bin/sh

export DJANGO_SETTINGS_MODULE=builtwithdjango.settings

opentelemetry-bootstrap -a install

python manage.py collectstatic --noinput
python manage.py migrate
# python manage.py djstripe_sync_models

python manage.py qcluster &



OTEL_RESOURCE_ATTRIBUTES=service.name=builtwithdjango
OTEL_EXPORTER_OTLP_ENDPOINT="$SIGNOZ_OTEL_COLLECTOR"

opentelemetry-instrument \
  --traces_exporter otlp_proto_http \
  --metrics_exporter otlp_proto_http \
  gunicorn --bind 0.0.0.0:80 --workers 3 builtwithdjango.wsgi:application
