include builtwithdjango/.env

export

export DJANGO_SETTINGS_MODULE=builtwithdjango.settings
export OTEL_SERVICE_NAME=$(SIGNOZ_SERVICE_NAME)
export OTEL_EXPORTER_OTLP_ENDPOINT=$(SIGNOZ_OTEL_COLLECTOR)
export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES

check-env:
	echo $(DEBUG)
	echo $(OTEL_EXPORTER_OTLP_ENDPOINT)
	echo $(STRIPE_TEST_SECRET_KEY)
.PHONY: check-env

runserver:
	poetry run opentelemetry-instrument \
		--traces_exporter otlp_proto_http \
		--metrics_exporter otlp_proto_http \
		python manage.py runserver --noreload
.PHONY: runserver

runprod:
	poetry run opentelemetry-instrument \
  --traces_exporter otlp_proto_http \
  --metrics_exporter otlp_proto_http \
  gunicorn \
		-c deployment/gunicorn.config.py \
    --bind 0.0.0.0:80 \
    --workers 3 \
    --reload \
    builtwithdjango.wsgi:application
.PHONY: runprod
