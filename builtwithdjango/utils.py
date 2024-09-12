import structlog


def get_builtwithdjango_logger(name):
    """This will add a `builtwithdjango` prefix to logger for easy configuration."""

    return structlog.get_logger(f"builtwithdjango.{name}")
