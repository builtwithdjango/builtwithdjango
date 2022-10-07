import json

import requests
from django.conf import settings


def add_email_to_revue(email, double_opt_in=True):
    data = {"email": str(email), "double_opt_in": double_opt_in}

    print(f"Adding {email} to Revue")
    r = requests.post(
        f"https://www.getrevue.co/api/v2/subscribers",
        headers={"Authorization": f"Token {settings.REVUE_API_TOKEN}"},
        json=data,
    )
    print(f"Done. Status: {r.status_code}")

    return r.json()
