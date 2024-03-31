#!/bin/sh

python manage.py collectstatic --noinput
python manage.py migrate
# python manage.py djstripe_sync_models

python manage.py qcluster &

export DJANGO_SETTINGS_MODULE=builtwithdjango.settings
export OTEL_SERVICE_NAME=builtwithdjango-dev
export OTEL_RESOURCE_ATTRIBUTES=service.name=builtwithdjango-dev
export OTEL_EXPORTER_OTLP_ENDPOINT=https://signoz-otel-collector-proxy.cr.lvtd.dev
export OTEL_EXPORTER_OTLP_PROTOCOL=http/protobuf

opentelemetry-instrument uvicorn --host 0.0.0.0 --port 80 builtwithdjango.asgi:application
