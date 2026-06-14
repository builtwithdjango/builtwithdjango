import os
import tempfile

import environ


def set_test_env(name, value):
    if os.environ.get(name) in {None, "", "''", '""'}:
        os.environ[name] = value


def env_flag(name):
    return os.environ.get(name, "").strip().lower() in {"1", "true", "yes", "on"}


set_test_env("ENV", "test")
set_test_env("SECRET_KEY", "test-secret-key")
set_test_env("DEBUG", "False")
set_test_env("SITE_URL", "http://localhost:8000")
set_test_env("ADMIN_URL", "admin/")
set_test_env("DATABASE_URL", "sqlite:///:memory:")
set_test_env("AWS_S3_ENDPOINT_URL", "http://localhost:9000")
set_test_env("AWS_ACCESS_KEY_ID", "test")
set_test_env("AWS_SECRET_ACCESS_KEY", "test")
set_test_env("EMAILOCTOPUS_API", "")
set_test_env("OCTO_LIST_ID", "")
set_test_env("REVUE_API_TOKEN", "")
set_test_env("BUTTONDOWN_API_TOKEN", "test-buttondown-token")
set_test_env("MAILGUN_API_KEY", "")
set_test_env("STRIPE_LIVE_SECRET_KEY", "sk_live_test")
set_test_env("STRIPE_TEST_SECRET_KEY", "sk_test_test")
set_test_env("STRIPE_LIVE_MODE", "False")
set_test_env("CLOUDINARY_CLOUD_NAME", "test")
set_test_env("CLOUDINARY_API_KEY", "test")
set_test_env("CLOUDINARY_API_SECRET", "test")
set_test_env("REDIS_URL", "redis://localhost:6379/0")
set_test_env("SCREENSHOT_API_KEY", "test-screenshot-key")
set_test_env("TJ_ALERTS_API_KEY", "test-tj-alerts-key")
set_test_env("JINA_READER_API_KEY", "test-jina-key")
set_test_env("GEMINI_API_KEY", "test-gemini-key")
set_test_env("OPENROUTER_API_KEY", "test-openrouter-key")
set_test_env("READWISE_API_TOKEN", "test-readwise-token")
set_test_env("POSTHOG_ENABLED", "False")

from .settings import *  # noqa: E402,F403

SECRET_KEY = "test-secret-key"
DEBUG = False
ALLOWED_HOSTS = ["testserver", "localhost", "127.0.0.1"]
CSRF_TRUSTED_ORIGINS = ["http://localhost:8000"]

if env_flag("DJANGO_TEST_USE_DATABASE_URL"):
    DATABASES = {
        "default": environ.Env.db_url_config(os.environ["DATABASE_URL"]),
    }
    if env_flag("DJANGO_TEST_REUSE_EXISTING_DATABASE"):
        DATABASES["default"]["TEST"] = {"NAME": DATABASES["default"]["NAME"]}
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": ":memory:",
        }
    }

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

MEDIA_ROOT = os.path.join(tempfile.gettempdir(), "builtwithdjango-test-media")
MEDIA_URL = "/media/"

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "builtwithdjango-tests",
    }
}

Q_CLUSTER = {
    **Q_CLUSTER,
    "sync": True,
}

POSTHOG_ENABLED = False

SILENCED_SYSTEM_CHECKS = [
    "staticfiles.W004",
    "templates.W003",
]
