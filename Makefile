.PHONY: serve manage makemigrations shell test test-pgsandbox bash test-webhook stripe-listen restart-worker prod-shell

serve:
	docker compose up -d --build
	docker compose logs -f backend

manage:
	docker compose run --rm backend python ./manage.py $(filter-out $@,$(MAKECMDGOALS))

makemigrations:
	docker compose run --rm backend python ./manage.py makemigrations

shell:
	docker compose run --rm backend python ./manage.py shell_plus --ipython

test:
	docker compose run --rm backend pytest $(ARGS)

test-pgsandbox:
	@test -n "$$DATABASE_URL" || (echo "DATABASE_URL is required. Create a pgsandbox database, then run: DATABASE_URL='postgresql://...' make test-pgsandbox"; exit 1)
	@pgsandbox_database_url=$$(printf '%s' "$$DATABASE_URL" | sed -e 's/@localhost\([:/]\)/@host.docker.internal\1/' -e 's/@127\.0\.0\.1\([:/]\)/@host.docker.internal\1/' -e 's/@\[::1\]\([:/]\)/@host.docker.internal\1/'); \
	docker compose run --rm --no-deps \
		-e DJANGO_TEST_USE_DATABASE_URL=true \
		-e DJANGO_TEST_REUSE_EXISTING_DATABASE=true \
		-e DATABASE_URL="$$pgsandbox_database_url" \
		backend pytest --reuse-db $(ARGS)

bash:
	docker compose run --rm backend bash

test-webhook:
	docker compose run --rm stripe trigger checkout.session.completed

stripe-listen:
	docker compose up stripe

restart-worker:
	docker compose up -d workers --force-recreate

prod-shell:
	./deployment/prod-shell.sh
