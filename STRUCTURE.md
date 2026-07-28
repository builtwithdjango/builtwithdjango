# Repository Structure

## Top-level map

- `builtwithdjango/` - Django settings, URL routing, analytics, logging,
  notifications, sitemaps, and shared utilities.
- `projects/` - project listings, ownership, likes, search/filter behavior,
  screenshot/content tasks, and project tests.
- `users/` - custom user model, profiles, account utilities, Stripe webhooks,
  and user tasks.
- `makers/` - legacy maker profiles and optional links to users.
- `blog/` - guides/articles, feeds, comments, publishing tasks, and Markdown
  rendering.
- `jobs/` - job and company models, listing/submission flows, feeds, and import
  tasks.
- `developers/` - developer directory, profiles, and pricing/access flows.
- `newsletter/` - subscription forms, email records, and delivery tasks.
- `podcast/` - episode models and public episode pages.
- `pages/` - landing, static, support, advertising, and other site pages.
- `api/` - DRF serializers, permissions, and API views.
- `tools/` - small public Django tools.
- `templates/` - app templates and shared server-rendered components.
- `frontend/src/` - Stimulus/Turbo code, Sentry entry point, and shared styles.
- `frontend/webpack/` - Webpack development, watch, and production configs.
- `frontend/vendors/` - source images, logos, and other bundled vendor assets.
- `deployment/` - Docker images, production entrypoint, Gunicorn, and shell
  helpers.
- `.github/workflows/` - Python/frontend CI, deployment, and automation.

## Placement rules

- Put domain models, forms, views, tasks, URLs, and tests in the Django app that
  owns the behavior.
- Put project-listing behavior in `projects/`; do not move ownership or
  publication rules into generic page views.
- Put account and subscription state in `users/`; keep the legacy `makers/`
  compatibility path narrow.
- Put shared site infrastructure in `builtwithdjango/` only when it is genuinely
  cross-app.
- Put templates in `templates/<app>/` and reusable fragments in
  `templates/components/`.
- Put shared browser controllers in `frontend/src/controllers/` and register
  them through the existing frontend application entry points.
- Put shared visual tokens and `bw-*` component classes in
  `frontend/src/styles/tailwind.css`.
- Put tests in the owning app's existing `tests.py` unless the module has
  already adopted a `tests/` package.

## Dependency rules

- Views may use forms, models, query helpers, and tasks from their own app.
- Keep authorization checks at the request boundary and back them with
  queryset/model constraints where needed.
- Avoid importing views from models, forms, tasks, or shared utilities.
- Keep queue task arguments serializable and prefer stable IDs over passing
  mutable model instances for new tasks.
- Reuse `builtwithdjango.analytics`, notification helpers, logging utilities,
  and Sentry helpers instead of creating per-app variants.
- Keep optional external integrations configurable so tests do not need live
  credentials.

## Existing patterns to follow

- Project public/owner queryset boundaries: `projects/views.py`.
- Project like annotations: `projects/querysets.py`.
- Project background lifecycle: `projects/tasks.py`.
- API permissions and analytics: `api/views.py`.
- Shared page shell and analytics initialization: `templates/base.html`.
- Reusable public cards and messages: `templates/components/`.
- Design tokens and component classes: `frontend/src/styles/tailwind.css`.
- Isolated test environment: `builtwithdjango/test_settings.py`.

## Special cases

- The project has both `Project.logged_in_maker` and the legacy
  `Project.maker.user` ownership path. Preserve both unless a dedicated
  migration removes the legacy relationship.
- Public project visibility is a lifecycle state, not simply record existence.
- Media uploads may depend on a queue worker and S3-compatible storage.
- Generated Webpack output is consumed by Django through an asset manifest; do
  not hand-edit build artifacts.
- Migrations are generated from model changes and excluded from automatic
  formatter hooks. Always inspect them manually.
