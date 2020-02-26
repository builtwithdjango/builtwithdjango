from django.db import models
from django.conf import settings
import requests

class Emails(models.Model):
    # Required Information
    user_email = models.EmailField()
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.user_email)

    def send_email_to_octopus(self):
        emailoctopus_api_key = settings.EMAILOCTOPUS_API
        list_id = "5ba12ae4-58c6-11ea-a3d0-06b4694bee2a"

        return requests.post(f"https://emailoctopus.com/api/1.5/lists/{list_id}/contacts?api_key={emailoctopus_api_key}",
                    data={"email_address":self.user_email})



