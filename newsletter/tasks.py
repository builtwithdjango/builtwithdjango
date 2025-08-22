import requests
import structlog
from django.conf import settings
from django.utils import timezone

from builtwithdjango.utils import get_builtwithdjango_logger
from newsletter.utils import generate_buttondown_newsletter_subject, prepare_newsletter

logger = get_builtwithdjango_logger(__name__)


def add_email_to_buttondown(email, tag, ip_address=None):
    data = {
        "email_address": str(email),
        "metadata": {"source": tag},
        "tags": [tag],
        "referrer_url": "https://builtwithdjango.com",
        "subscriber_type": "unactivated",
    }

    if ip_address:
        data["ip_address"] = ip_address
    if tag == "user":
        data["type"] = "regular"

    r = requests.post(
        f"https://api.buttondown.email/v1/subscribers",
        headers={"Authorization": f"Token {settings.BUTTONDOWN_API_TOKEN}", "X-API-Version": "2025-06-01"},
        json=data,
    )

    try:
        response_data = r.json() if r.text.strip() else {}
    except requests.exceptions.JSONDecodeError:
        response_data = {"error": "Non-JSON response", "content": r.text}

    log_context = {
        "email": email,
        "tag": tag,
        "ip_address": ip_address,
        "status_code": r.status_code,
        "response_data": response_data,
        "response_text": r.text[:500] if r.text else None,
    }

    logger.info("Buttondown API response", **log_context)

    # Return structured response
    if r.status_code in [200, 201]:
        return {"success": True, "data": response_data}
    else:
        return {"success": False, "status_code": r.status_code, "error_data": response_data}


def send_buttondown_newsletter():
    now = timezone.now()
    nine_am_today = now.replace(hour=9, minute=0, second=0, microsecond=0)
    publish_date = nine_am_today.isoformat()

    body = prepare_newsletter()
    subject = generate_buttondown_newsletter_subject(body)

    url = "https://api.buttondown.com/v1/emails"
    headers = {"Authorization": f"Token {settings.BUTTONDOWN_API_TOKEN}"}
    data = {"subject": subject, "body": body, "publish_date": publish_date}

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200 or response.status_code == 201:
        return "Success"
    else:
        response.raise_for_status()
