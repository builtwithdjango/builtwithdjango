import requests
from django.conf import settings
from django.db import models


class Emails(models.Model):
    # Required Information
    user_email = models.EmailField()
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.user_email)
