#!/bin/sh

# Default to server command if no arguments provided
if [ $# -eq 0 ]; then
    echo "No arguments provided. Defaulting to running the server."
    server=true
else
    server=false
fi

# All commands before the conditional ones
export DJANGO_SETTINGS_MODULE=builtwithdjango.settings
export OTEL_EXPORTER_OTLP_ENDPOINT=https://signoz-otel-collector-proxy.cr.lvtd.dev
export OTEL_EXPORTER_OTLP_PROTOCOL=http/protobuf

python manage.py collectstatic --noinput
python manage.py migrate
# Parse command-line arguments
while getopts ":sw" option; do
    case "${option}" in
        s)  # Run server
            server=true
            ;;
        w)  # Run worker
            server=false
            ;;
        *)  # Invalid option
            echo "Invalid option: -$OPTARG" >&2
            ;;
    esac
done
shift $((OPTIND - 1))

# If no valid option provided, default to server
if [ "$server" = true ]; then
    # python manage.py djstripe_sync_models
    export OTEL_SERVICE_NAME=builtwithdjango_${ENV:-dev}
    export OTEL_RESOURCE_ATTRIBUTES=service.name=builtwithdjango_${ENV:-dev}
    opentelemetry-instrument gunicorn builtwithdjango.asgi:application -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:80 --workers 3
else
    export OTEL_SERVICE_NAME="builtwithdjango_${ENV:-dev}_workers"
    export OTEL_RESOURCE_ATTRIBUTES=service.name=builtwithdjango_${ENV:-dev}_workers
    opentelemetry-instrument python manage.py qcluster
fi
