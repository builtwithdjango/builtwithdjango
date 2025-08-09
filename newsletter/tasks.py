import requests
from django.conf import settings
from django.utils import timezone

from newsletter.utils import generate_buttondown_newsletter_subject, prepare_newsletter


def add_email_to_buttondown(email, tag):
    data = {
        "email": str(email),
        "metadata": {"source": tag},
        "tags": [tag],
        "referrer_url": "https://builtwithdjango.com",
        "subscriber_type": "unactivated",
    }
    if tag == "user":
        data["subscriber_type"] = "regular"

    r = requests.post(
        f"https://api.buttondown.email/v1/subscribers",
        headers={"Authorization": f"Token {settings.BUTTONDOWN_API_TOKEN}"},
        json=data,
    )

    return r.json()


def send_buttondown_newsletter():
    now = timezone.now()
    nine_am_today = now.replace(hour=9, minute=0, second=0, microsecond=0)
    publish_date = nine_am_today.isoformat()

    body = prepare_newsletter()
    subject = generate_buttondown_newsletter_subject(body)

    url = "https://api.buttondown.com/v1/emails"
    headers = {"Authorization": f"Token {settings.BUTTONDOWN_API_KEY}"}
    data = {"subject": subject, "body": body, "publish_date": publish_date}

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200 or response.status_code == 201:
        return "Success"
    else:
        response.raise_for_status()
