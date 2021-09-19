from django.db import models
from model_utils.models import TimeStampedModel


class CistercianDateNftRequest(TimeStampedModel):
    email = models.EmailField(unique=True)
    email_confirmed = models.BooleanField(default=False)
    wallet_public_key = models.CharField(max_length=200, unique=True)
    date_requested = models.DateField(unique=True)
    sent = models.BooleanField(default=False)
    proof = models.URLField(blank=True)
    link = models.URLField(blank=True)

    def __str__(self):
        return f"{self.date_requested}"
