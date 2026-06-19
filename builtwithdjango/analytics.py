import hashlib
import re
import time
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

import posthog
from django.conf import settings

from builtwithdjango.utils import get_builtwithdjango_logger

logger = get_builtwithdjango_logger(__name__)

_CONTROL_CHARS_RE = re.compile(r"[\x00-\x1f\x7f-\x9f]")
_SENSITIVE_KEY_RE = re.compile(
    r"(password|passwd|pwd|secret|csrf|authorization|cookie|sessionid|api[_-]?key|apikey|"
    r"private[_-]?key|access[_-]?key|refresh[_-]?token|auth[_-]?token|id[_-]?token|"
    r"stripe[_-]?secret|card[_-]?number|cvv|dsn)",
    re.IGNORECASE,
)
_SENSITIVE_QUERY_RE = re.compile(r"(token|auth|code|email|session|key|signature|password)", re.IGNORECASE)
_ALLOWED_SENSITIVE_KEYS = {"$session_id", "distinct_id"}
_MAX_HEADER_LENGTH = 1000


def posthog_template_context(request):
    return {
        "app_environment": getattr(settings, "ENVIRONMENT", ""),
        "posthog_enabled": getattr(settings, "POSTHOG_ENABLED", False),
        "posthog_api_key": getattr(settings, "POSTHOG_API_KEY", ""),
        "posthog_api_host": getattr(settings, "POSTHOG_HOST", "https://us.i.posthog.com"),
        "posthog_ui_host": getattr(settings, "POSTHOG_UI_HOST", "https://us.posthog.com"),
        "posthog_js_defaults": getattr(settings, "POSTHOG_JS_DEFAULTS", "2026-01-30"),
        "posthog_environment": getattr(settings, "ENVIRONMENT", ""),
    }


def posthog_request_filter(request):
    if not getattr(settings, "POSTHOG_ENABLED", False):
        return False

    path = request.path or ""
    if _is_noisy_analytics_request_path(path):
        return False

    admin_url = "/" + getattr(settings, "ADMIN_URL", "admin/").lstrip("/")
    skipped_prefixes = (
        admin_url,
        "/static/",
        "/media/",
        "/favicon",
        "/robots.txt",
        "/sitemap",
        "/health",
        "/__debug__",
    )

    return not path.startswith(skipped_prefixes)


def _is_noisy_analytics_request_path(path):
    return path == "/api/v1/like" or path.startswith("/api/v1/like/")


def posthog_extra_tags(request):
    user = getattr(request, "user", None)
    user_is_authenticated = _user_is_authenticated(user)
    resolver_match = getattr(request, "resolver_match", None)
    tags = {
        "app": "builtwithdjango",
        "environment": getattr(settings, "ENVIRONMENT", ""),
        "user_type": "authenticated" if user_is_authenticated else "anonymous",
    }

    if resolver_match:
        tags.update(
            {
                "route": resolver_match.route,
                "url_name": resolver_match.url_name,
                "view_name": getattr(resolver_match.func, "__name__", ""),
                "app_names": resolver_match.app_names,
            }
        )

    if user_is_authenticated:
        tags.update(
            {
                "user_id": str(user.pk),
                "username": getattr(user, "username", ""),
                "subscription_level": getattr(user, "subscription_level", ""),
                "has_active_django_devs_subscription": getattr(user, "has_active_django_devs_subscription", False),
                "is_staff": getattr(user, "is_staff", False),
                "is_superuser": getattr(user, "is_superuser", False),
            }
        )

    return tags


def posthog_before_send(message):
    return _scrub_value(message)


def capture(request, event, properties=None, groups=None, distinct_id=None):
    if not getattr(settings, "POSTHOG_ENABLED", False):
        return None

    event_properties = {}
    if request is not None:
        event_properties.update(get_request_properties(request))

        session_id = get_request_session_id(request)
        if session_id:
            event_properties["$session_id"] = session_id

        user = getattr(request, "user", None)
        if _user_is_authenticated(user):
            event_properties["$set"] = get_user_properties(user)

    if properties:
        event_properties.update(properties)

    resolved_distinct_id = distinct_id
    if resolved_distinct_id is None and request is not None:
        resolved_distinct_id = get_request_distinct_id(request)

    kwargs = {"properties": event_properties}
    if resolved_distinct_id:
        kwargs["distinct_id"] = resolved_distinct_id
    if groups:
        kwargs["groups"] = groups
    if request is not None and get_client_ip(request):
        kwargs["disable_geoip"] = False

    try:
        return posthog.capture(event, **kwargs)
    except Exception as exc:
        logger.warning("posthog_capture_failed", event=event, error=str(exc))
        return None


def capture_event(event, properties=None, distinct_id=None, groups=None):
    if not getattr(settings, "POSTHOG_ENABLED", False):
        return None

    event_properties = properties or {}
    resolved_distinct_id = distinct_id or get_event_distinct_id(event, event_properties)
    if not resolved_distinct_id:
        logger.warning("posthog_capture_without_distinct_id", event=event)
        return None

    kwargs = {
        "properties": event_properties,
        "distinct_id": resolved_distinct_id,
    }
    if groups:
        kwargs["groups"] = groups

    try:
        return posthog.capture(event, **kwargs)
    except Exception as exc:
        logger.warning("posthog_capture_failed", event=event, error=str(exc))
        return None


def capture_checkout_return(request, checkout_surface):
    session_id = _sanitize_identifier(request.GET.get("session_id"))
    status = _sanitize_identifier(request.GET.get("status"))

    if session_id:
        capture(
            request,
            "checkout returned",
            properties={
                "checkout_surface": checkout_surface,
                "checkout_status": "success",
                "stripe_checkout_session_id": session_id,
            },
        )
    elif status == "failed":
        capture(
            request,
            "checkout canceled",
            properties={
                "checkout_surface": checkout_surface,
                "checkout_status": status,
            },
        )


def get_request_properties(request):
    resolver_match = getattr(request, "resolver_match", None)
    properties = {
        "request_path": request.path,
        "request_method": request.method,
        "request_query_keys": sorted(request.GET.keys()),
        "request_query_count": len(request.GET),
        "request_content_type": request.META.get("CONTENT_TYPE", ""),
        "request_content_length": request.META.get("CONTENT_LENGTH", ""),
        "referrer": redact_url(request.META.get("HTTP_REFERER", "")),
        "is_ajax": request.headers.get("X-Requested-With") == "XMLHttpRequest",
        "is_secure": request.is_secure(),
    }

    if resolver_match:
        properties.update(
            {
                "route": resolver_match.route,
                "url_name": resolver_match.url_name,
                "view_name": getattr(resolver_match.func, "__name__", ""),
            }
        )

    if request.method in {"POST", "PUT", "PATCH"}:
        submitted_fields = [
            field
            for field in get_post_keys(request)
            if not field.startswith("_posthog") and field.lower() != "csrfmiddlewaretoken"
        ]
        properties["submitted_field_keys"] = sorted(submitted_fields)
        properties["submitted_field_count"] = len(submitted_fields)

    user = getattr(request, "user", None)
    if _user_is_authenticated(user):
        properties["user_id"] = str(user.pk)
        properties["user_authenticated"] = True
    else:
        properties["user_authenticated"] = False

    return properties


def get_user_properties(user):
    date_joined = getattr(user, "date_joined", None)
    return {
        "email": getattr(user, "email", ""),
        "username": getattr(user, "username", ""),
        "first_name": getattr(user, "first_name", ""),
        "last_name": getattr(user, "last_name", ""),
        "subscription_level": getattr(user, "subscription_level", ""),
        "has_active_django_devs_subscription": getattr(user, "has_active_django_devs_subscription", False),
        "make_public": getattr(user, "make_public", None),
        "is_staff": getattr(user, "is_staff", False),
        "is_superuser": getattr(user, "is_superuser", False),
        "date_joined": date_joined.isoformat() if date_joined else None,
    }


def get_request_distinct_id(request):
    user = getattr(request, "user", None)
    if _user_is_authenticated(user):
        return str(user.pk)

    post_value = _sanitize_identifier(get_post_value(request, "_posthog_distinct_id"))
    if post_value:
        return post_value

    header_value = _sanitize_identifier(request.headers.get("X-POSTHOG-DISTINCT-ID"))
    if header_value:
        return header_value

    return get_anonymous_distinct_id(request)


def get_anonymous_distinct_id(request):
    session = getattr(request, "session", None)
    session_key = getattr(session, "session_key", None)
    if session_key:
        return f"anonymous_session:{stable_hash(session_key)}"

    fingerprint_parts = [
        get_client_ip(request),
        request.META.get("HTTP_USER_AGENT", ""),
        request.META.get("HTTP_ACCEPT_LANGUAGE", ""),
    ]
    fingerprint = "|".join(part or "" for part in fingerprint_parts)
    if fingerprint.strip("|"):
        return f"anonymous_request:{stable_hash(fingerprint)}"

    return None


def get_request_session_id(request):
    header_value = _sanitize_identifier(request.headers.get("X-POSTHOG-SESSION-ID"))
    if header_value:
        return header_value

    return _sanitize_identifier(get_post_value(request, "_posthog_session_id"))


def get_event_distinct_id(event, properties):
    fallback_keys = (
        ("user_id", "user"),
        ("job_id", "job"),
        ("project_id", "project"),
        ("stripe_customer_id", "stripe_customer"),
        ("stripe_checkout_session_id", "stripe_checkout"),
        ("stripe_event_id", "stripe_event"),
    )

    for key, prefix in fallback_keys:
        value = properties.get(key)
        if value:
            return _sanitize_identifier(f"{prefix}:{value}")

    if event:
        return _sanitize_identifier(f"server:{stable_hash(event)}")

    return None


def get_client_ip(request):
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()

    return request.META.get("REMOTE_ADDR")


def get_post_value(request, key):
    try:
        return request.POST.get(key)
    except Exception as exc:
        logger.debug("posthog_post_value_unavailable", key=key, error=str(exc))
        return None


def get_post_keys(request):
    try:
        return request.POST.keys()
    except Exception as exc:
        logger.debug("posthog_post_keys_unavailable", error=str(exc))
        return []


def email_domain(email):
    if not email or "@" not in email:
        return ""

    return email.rsplit("@", 1)[1].lower()


def stable_hash(value):
    if value is None:
        return ""

    return hashlib.sha256(str(value).strip().lower().encode("utf-8")).hexdigest()[:16]


def redact_url(url):
    if not url:
        return url

    try:
        parsed = urlsplit(str(url))
    except ValueError:
        return "[REDACTED_URL]"

    query_params = []
    for key, value in parse_qsl(parsed.query, keep_blank_values=True):
        if _SENSITIVE_QUERY_RE.search(key):
            query_params.append((key, "[REDACTED]"))
        else:
            query_params.append((key, value))

    return urlunsplit((parsed.scheme, parsed.netloc, parsed.path, urlencode(query_params), parsed.fragment))


class AnalyticsRequestMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        started_at = time.perf_counter()

        try:
            response = self.get_response(request)
        except Exception as exc:
            self._capture_request(request, started_at, "request failed", exception=exc)
            raise

        self._capture_request(request, started_at, "request completed", response=response)
        return response

    def _capture_request(self, request, started_at, event, response=None, exception=None):
        if not posthog_request_filter(request):
            return

        properties = {
            "duration_ms": round((time.perf_counter() - started_at) * 1000, 2),
        }
        if response is not None:
            properties.update(
                {
                    "status_code": response.status_code,
                    "response_content_type": response.get("Content-Type", ""),
                    "response_content_length": response.get("Content-Length", ""),
                }
            )
        if exception is not None:
            properties.update(
                {
                    "exception_type": exception.__class__.__name__,
                    "exception_message": "[REDACTED]",
                    "exception_message_hash": stable_hash(str(exception)),
                }
            )

        capture(request, event, properties=properties)


def _sanitize_identifier(value):
    if not isinstance(value, str) or not value:
        return None

    sanitized = _CONTROL_CHARS_RE.sub("", value).strip()[:_MAX_HEADER_LENGTH]
    return sanitized or None


def _user_is_authenticated(user):
    if user is None:
        return False

    is_authenticated = getattr(user, "is_authenticated", False)
    if callable(is_authenticated):
        return is_authenticated()

    return bool(is_authenticated)


def _scrub_value(value):
    if isinstance(value, dict):
        scrubbed = {}
        for key, inner_value in value.items():
            key_string = str(key)
            if key_string not in _ALLOWED_SENSITIVE_KEYS and _SENSITIVE_KEY_RE.search(key_string):
                scrubbed[key] = "[REDACTED]"
            else:
                scrubbed[key] = _scrub_value(inner_value)
        return scrubbed

    if isinstance(value, list):
        return [_scrub_value(item) for item in value]

    if isinstance(value, tuple):
        return tuple(_scrub_value(item) for item in value)

    if isinstance(value, str) and (value.startswith("http://") or value.startswith("https://")):
        return redact_url(value)

    return value
