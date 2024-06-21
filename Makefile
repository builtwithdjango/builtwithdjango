include builtwithdjango/.env

export

export DJANGO_SETTINGS_MODULE=builtwithdjango.settings
export OTEL_SERVICE_NAME=$(SIGNOZ_SERVICE_NAME)
export OTEL_EXPORTER_OTLP_ENDPOINT=$(SIGNOZ_OTEL_COLLECTOR)
export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES

redis:
	redis-stack-server --port 6390

check-env:
	echo $(DEBUG)
	echo $(OTEL_EXPORTER_OTLP_ENDPOINT)
	echo $(STRIPE_TEST_SECRET_KEY)
.PHONY: check-env


shell:
	poetry run python manage.py shell_plus --ipython


prod-shell:
	./deployment/prod-shell.sh
