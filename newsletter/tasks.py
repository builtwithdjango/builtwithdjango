import requests
from django.conf import settings


def add_email_to_revue(instance):
    requests.post(
        f"https://www.getrevue.co/api/v2/subscribers",
        headers={"Authorization": f"Token {settings.REVUE_API_TOKEN}"},
        data={"email": instance.user_email},
    )
