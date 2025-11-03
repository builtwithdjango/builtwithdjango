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


def send_buttondown_newsletter(days_back: int = 7):
    """
    Create a draft newsletter via Buttondown API.

    Args:
        days_back: Number of days to look back for content. Defaults to 7.
    """
    logger.info("Preparing newsletter draft with content from the last %d days", days_back)

    # Prepare newsletter with content from the specified number of days
    body = prepare_newsletter(days_back=days_back)
    subject = generate_buttondown_newsletter_subject(body)

    url = "https://api.buttondown.com/v1/emails"
    headers = {"Authorization": f"Token {settings.BUTTONDOWN_API_TOKEN}"}
    # Omitting publish_date creates a draft instead of scheduling the email
    data = {"subject": subject, "body": body, "status": "draft"}

    r = requests.post(url, headers=headers, json=data)

    logger.info("Newsletter draft created successfully", subject=subject, days_back=days_back)
    return "Success"
