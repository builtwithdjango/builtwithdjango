include builtwithdjango/.env

export

check-env:
	echo $(DEBUG)
	echo $(OTEL_EXPORTER_OTLP_ENDPOINT)
	echo $(STRIPE_TEST_SECRET_KEY)
.PHONY: check-env


shell:
	poetry run python manage.py shell_plus --ipython


prod-shell:
	./deployment/prod-shell.sh
