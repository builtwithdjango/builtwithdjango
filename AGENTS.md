# AGENTS.md

## Scope

This is the canonical, tool-neutral operating guide for coding agents working
on Built with Django. Read it before editing, then use `PRODUCT.md`, `TECH.md`,
`STRUCTURE.md`, and `DESIGN.md` for deeper product, technical, repository, and
interface context.

Do not add vendor-specific instruction files that duplicate this guidance.
Add a nested `AGENTS.md` only when a subdirectory needs genuinely scoped rules.

## Project summary

Built with Django is a community showcase and learning hub for real products
built with Django. The main public paths are projects, practical guides, jobs,
developers, makers, podcast episodes, and supporting resources.

Registered users can submit projects. A submitted project is linked to that
account through `Project.logged_in_maker`; linked submitters can update their
project metadata and screenshot. Public discovery remains curated: project
lists show only published, active, non-spam records.

## Workflow

- Read the relevant steering files and nearby implementation before editing.
- Prefer `rg` and `rg --files` for repository search.
- Keep changes inside the app boundaries documented in `STRUCTURE.md`.
- Use Django conventions and existing forms, views, model methods, template
  tags, and tasks before introducing a new abstraction.
- Keep business logic out of templates.
- Change models first, then generate migrations with `make makemigrations`.
  Inspect generated migrations; do not hand-edit historical migrations.
- Add or update tests for features, bug fixes, authorization changes, queue
  behavior, and risky refactors.
- Update `CHANGELOG.md` under `Unreleased` for material user-facing or
  operational changes. Skip entries for tests, formatting, and internal-only
  refactors.
- Preserve unrelated user changes in a dirty worktree.

## Commands

Docker-backed development:

```bash
make serve
make shell
make makemigrations
make restart-worker
```

Tests and checks:

```bash
make test
make test ARGS="projects/tests.py -q"
docker compose run --rm --no-deps backend pytest
docker compose run --rm --no-deps backend python manage.py check --settings=builtwithdjango.test_settings
docker compose run --rm --no-deps backend python manage.py makemigrations --check --dry-run --settings=builtwithdjango.test_settings
```

When another project already owns a Compose dependency port, use the
`--no-deps` pytest command; `builtwithdjango.test_settings` provides isolated
test storage and does not require the development Postgres or Redis services.

Frontend:

```bash
npm ci
npm run build
```

Use Node 22 for host frontend work (`.nvmrc`). CI also verifies the frontend
with Node 18. The supported backend test path is Docker-backed `make test`;
host pytest is mainly for deliberately reproducing the CI environment.

## Verification

- Run the smallest relevant test target while iterating, then broaden when a
  change affects shared auth, settings, models, middleware, or templates.
- Before handoff, run `git diff --check`.
- For model changes, verify migration drift with
  `makemigrations --check --dry-run`.
- For template or frontend changes, run `npm run build` and inspect the affected
  page in a browser at mobile and desktop widths.
- For project submission changes, test the submitter, another authenticated
  user, an anonymous user, and staff-visible behavior as applicable.
- For background work, run a Django Q2 worker (`make restart-worker` or
  `python manage.py qcluster` in the same configured environment), wait only a
  bounded time, and verify both the task result and resulting database state.

## Local development safety

- Before binding any local server or service, check whether its preferred port
  is already in use.
- If a port is occupied, leave the existing process or container untouched and
  bind this repository to another available port.
- Report the actual local URL, including the selected port, when handing off a
  preview.
- Do not stop, replace, or reconfigure another repository's containers to make
  room for this project.

## Product and security guardrails

- Keep public project queries constrained to published, active, non-spam
  projects unless the route is explicitly an owner or staff preview.
- Treat project ownership as an authorization boundary. A matching legacy
  email address alone does not establish ownership.
- Do not expose unpublished projects to anonymous visitors.
- Project publication depends on background screenshot processing. When
  diagnosing a missing submission, inspect the Django Q queue, worker, storage
  upload, and final `published` state.
- Keep API mutation permissions explicit. Blog post API writes are restricted
  to token-authenticated superusers.
- Never print, log, commit, or place in screenshots API keys, OAuth tokens,
  session data, private form contents, or `.env` values.
- Keep optional integrations behind settings checks so focused local
  development and tests work without production credentials.
- Ask before destructive production data actions or deleting generated/user
  media outside the requested scope.

## Code and interface conventions

- Python formatting uses Black and isort with 120-character lines.
- Tests use pytest with `builtwithdjango.test_settings`; test files live in each
  Django app using the existing `tests.py` convention.
- Use Django templates and Tailwind utilities for server-rendered pages.
- Use the existing Stimulus/Turbo controllers in `frontend/src` for shared
  browser behavior; Alpine.js is already loaded for small local template state.
- Reuse the `bw-*` component classes and CSS variables in
  `frontend/src/styles/tailwind.css`. Follow `DESIGN.md` before changing the
  visual language.
- Preserve accessible labels, keyboard focus, reduced-motion behavior, and
  mobile layouts.

## Git

- Worktrees may contain uncommitted user work. Do not revert unrelated files.
- Use a descriptive branch name that follows the user's current convention when
  a branch is requested.
- Do not force-push or rewrite shared history unless explicitly asked.
