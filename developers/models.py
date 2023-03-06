import pytz
from django.conf import settings
from django.db import models
from django.urls import reverse
from model_utils.models import TimeStampedModel


class Developer(TimeStampedModel):
    looking_for_a_job = models.BooleanField(default=False)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="developer")

    title = models.CharField(max_length=256)
    description = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=[("LOOKING", "Actively Looking"), ("OPEN", "Open to Offers"), ("BUSY", "Currently Busy")],
        default="OPEN",
    )

    role = models.CharField(
        max_length=20,
        choices=[("JUNIOR", "Junior"), ("MID", "Mid"), ("SENIOR", "Senior")],
        default="MID",
    )

    # comma separated list (from multiple choice)
    capacity = models.TextField(blank=True)

    # Geo
    location = models.CharField(max_length=50)  # City, Country
    TIMEZONES = tuple(zip(pytz.all_timezones, pytz.all_timezones))
    timezone = models.CharField(max_length=32, choices=TIMEZONES, default="UTC")

    def __str__(self):
        return self.user.username

    def get_absolute_url(self):
        return reverse("developer", kwargs={"slug": self.user.slug})
