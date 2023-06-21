include builtwithdjango/.env

runserver:
	DJANGO_SETTINGS_MODULE=builtwithdjango.settings
	OTEL_RESOURCE_ATTRIBUTES=service.name=bwd_local
	OTEL_EXPORTER_OTLP_ENDPOINT="$(SIGNOZ_OTEL_COLLECTOR)"
	poetry run opentelemetry-instrument \
		--traces_exporter otlp_proto_http \
		--metrics_exporter otlp_proto_http \
		python manage.py runserver --noreload
.PHONY: runserver
