from django.db import models
from django.conf import settings
import requests


class Emails(models.Model):
    # Required Information
    user_email = models.EmailField()
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.user_email)
