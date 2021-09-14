from django.db import models
from model_utils.models import TimeStampedModel


class CistercianDateNftRequest(TimeStampedModel):
    email = models.EmailField(unique=True)
    wallet_public_key = models.CharField(max_length=200, unique=True)
    date_requested = models.DateField(unique=True)
    sent = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.email}-{self.date_requested}"
