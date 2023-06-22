#!/bin/sh

python manage.py collectstatic --noinput
python manage.py migrate
# python manage.py djstripe_sync_models

python manage.py qcluster &

echo "$(SIGNOZ_SERVICE_NAME)"

export DJANGO_SETTINGS_MODULE=builtwithdjango.settings
export OTEL_SERVICE_NAME=$(SIGNOZ_SERVICE_NAME)
export OTEL_EXPORTER_OTLP_ENDPOINT=$(SIGNOZ_OTEL_COLLECTOR)

# gunicorn --bind 0.0.0.0:80 --workers 3 builtwithdjango.wsgi:application

opentelemetry-instrument \
  --traces_exporter otlp_proto_http \
  --metrics_exporter otlp_proto_http \
  gunicorn \
    -c deployment/gunicorn.config.py \
    --bind 0.0.0.0:80 \
    --workers 3 \
    --reload \
    builtwithdjango.wsgi:application
