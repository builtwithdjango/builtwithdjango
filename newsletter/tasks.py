import json

import requests
from django.conf import settings


def add_email_to_buttondown(email, tag):
    data = {
        "email": str(email),
        "metadata": {"source": tag},
        "tags": [tag],
    }
    r = requests.post(
        f"https://www.getrevue.co/api/v2/subscribers",
        headers={"Authorization": f"Token {settings.REVUE_API_TOKEN}"},
        json=data,
    )

    return r.json()
