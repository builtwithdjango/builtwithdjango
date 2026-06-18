---
name: blog-post-management-api
description: Use when an AI agent needs to manage Built With Django blog posts through the site API, including creating, reading, listing, updating, or deleting posts. Covers the superuser-token-only CRUD endpoints under /api/v1/posts/, required headers, payload fields, status/type/level choices, tag behavior, safety checks, and troubleshooting for permission or validation errors.
---

# Blog Post Management API

Use the Built With Django blog post API to manage posts programmatically. These endpoints are for automation by trusted agents only and require a token/API key that belongs to a Django superuser.

## Auth

Always send the superuser token in the DRF token header:

```bash
Authorization: Token $SUPERUSER_API_KEY
```

Do not use session cookies, browser login state, or a staff-only token. The API intentionally accepts `TokenAuthentication` only and checks `user.is_superuser`.

Keep tokens out of source files, issue comments, logs, and PR descriptions. Read them from the runtime environment or a secret manager. If a token is missing or belongs to a non-superuser, stop and ask for a proper superuser API token instead of trying to work around the permission failure.

## Endpoints

Base path:

```text
/api/v1/posts/
```

Supported operations:

| Operation | Method and path | Notes |
|---|---|---|
| List posts | `GET /api/v1/posts/` | Returns drafts and published posts visible to the superuser token. |
| Filter posts | `GET /api/v1/posts/?status=PB&type=TUTORIAL&level=BEGINNER` | Supported filters: `status`, `type`, `level`. |
| Create post | `POST /api/v1/posts/` | Assigns `author` from the superuser token. |
| Read post | `GET /api/v1/posts/{id}/` | Returns one post by numeric id. |
| Update post | `PATCH /api/v1/posts/{id}/` | Prefer `PATCH` for partial edits. |
| Replace post | `PUT /api/v1/posts/{id}/` | Use only when sending all required fields. |
| Delete post | `DELETE /api/v1/posts/{id}/` | Permanently deletes the post. Read first unless the user gave an exact id. |

## Fields

Writable fields:

| Field | Values |
|---|---|
| `title` | Post title. |
| `description` | Optional summary text. |
| `slug` | URL slug. Check existing posts before changing it. |
| `content` | Full post body. |
| `status` | `DR` for draft, `PB` for published. |
| `type` | `TUTORIAL`, `INTERVIEW`, `UPDATE`, or `ARTICLE`. |
| `level` | `BEGINNER`, `INTERMEDIATE`, or `ADVANCED`. |
| `unsplashID` | Optional Unsplash image id. |
| `tags` | Comma-separated string, for example `Django, Testing`. |

Read-only response fields include `id`, `author`, `created`, `modified`, and `tag_list`.

Tag behavior:

- On create, non-empty `tags` creates or reuses tags by slug and attaches them.
- On update, non-empty `tags` replaces the full tag set.
- Omitted `tags` leaves tags unchanged.
- Blank `tags` is treated as no-op. Do not send `tags: ""` expecting tags to be cleared.

## Request Examples

Set these first:

```bash
export SITE_BASE_URL="https://builtwithdjango.com"
export SUPERUSER_API_KEY="..."
```

List posts:

```bash
curl -sS "$SITE_BASE_URL/api/v1/posts/" \
  -H "Authorization: Token $SUPERUSER_API_KEY"
```

Create a draft:

```bash
curl -sS -X POST "$SITE_BASE_URL/api/v1/posts/" \
  -H "Authorization: Token $SUPERUSER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Testing Django Agents",
    "description": "A short guide to testing agent-managed Django workflows.",
    "slug": "testing-django-agents",
    "content": "Draft content goes here.",
    "status": "DR",
    "type": "TUTORIAL",
    "level": "INTERMEDIATE",
    "tags": "Django, Testing, Agents",
    "unsplashID": "example-image-id"
  }'
```

Update selected fields:

```bash
curl -sS -X PATCH "$SITE_BASE_URL/api/v1/posts/123/" \
  -H "Authorization: Token $SUPERUSER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Updated title",
    "status": "PB"
  }'
```

Replace tags:

```bash
curl -sS -X PATCH "$SITE_BASE_URL/api/v1/posts/123/" \
  -H "Authorization: Token $SUPERUSER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"tags": "Django, API"}'
```

Delete a post:

```bash
curl -sS -i -X DELETE "$SITE_BASE_URL/api/v1/posts/123/" \
  -H "Authorization: Token $SUPERUSER_API_KEY"
```

## Agent Workflow

1. Confirm the target environment and load `SITE_BASE_URL` and `SUPERUSER_API_KEY` from trusted configuration.
2. For updates or deletes, fetch the post first and verify the `id`, `title`, `slug`, and `status`.
3. Prefer draft status (`DR`) for newly generated content unless the user explicitly asks to publish.
4. Use `PATCH` for edits so omitted fields remain unchanged.
5. After create, update, or delete, read back the relevant list or detail endpoint to confirm the final state.
6. Report the post id, slug, status, and changed fields. Do not print the token.

## Troubleshooting

- `401` or `403`: token is missing, invalid, not sent as `Authorization: Token ...`, or does not belong to a superuser.
- `400`: check required fields and allowed choices for `status`, `type`, and `level`.
- `404`: the post id does not exist, or the path is not `/api/v1/posts/{id}/`.
- Session-authenticated requests are expected to fail. Use the superuser token header.
