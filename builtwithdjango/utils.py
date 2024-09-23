import structlog


def get_builtwithdjango_logger(name):
    """This will add a `builtwithdjango` prefix to logger for easy configuration."""

    return structlog.get_logger(f"builtwithdjango.{name}")


def before_send(event, hint):
    if "exc_info" in hint:
        _, _, tb = hint["exc_info"]

        if is_opentelemetry_error(tb):
            print("Ignoing Opentelemetry Error")
            return None

    return event


def is_opentelemetry_error(tb):
    while tb:
        filename = tb.tb_frame.f_code.co_filename
        if "opentelemetry" in filename:
            return True
        tb = tb.tb_next
    return False
