import requests
from django.conf import settings
from django.utils import timezone

from newsletter.utils import generate_buttondown_newsletter_subject, prepare_newsletter


def add_email_to_buttondown(email, tag, ip_address=None):
    data = {
        "email": str(email),
        "metadata": {"source": tag},
        "tags": [tag],
        "referrer_url": "https://builtwithdjango.com",
        "subscriber_type": "unactivated",
    }

    # Add IP address to metadata if provided
    if ip_address:
        data["metadata"]["ip_address"] = ip_address
    if tag == "user":
        data["subscriber_type"] = "regular"

    r = requests.post(
        f"https://api.buttondown.email/v1/subscribers",
        headers={"Authorization": f"Token {settings.BUTTONDOWN_API_TOKEN}"},
        json=data,
    )

    # Check if the response is successful
    if r.status_code in [200, 201]:
        # Check if the response has content before parsing JSON
        if r.text.strip():
            try:
                return r.json()
            except requests.exceptions.JSONDecodeError:
                # If JSON parsing fails, return the text content
                return {"error": "Invalid JSON response", "content": r.text}
        else:
            # Empty response but successful status code
            return {"success": True, "message": "Email added successfully"}
    else:
        # Handle error responses
        try:
            error_data = r.json() if r.text.strip() else {"error": "Empty error response"}
        except requests.exceptions.JSONDecodeError:
            error_data = {"error": "Non-JSON error response", "content": r.text}

        raise Exception(f"Buttondown API error (status {r.status_code}): {error_data}")


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
