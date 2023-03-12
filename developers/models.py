import uuid

import pytz
from django.conf import settings
from django.db import models
from django.urls import reverse
from model_utils.models import TimeStampedModel


class Developer(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    looking_for_a_job = models.BooleanField(default=False)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="developer")

    title = models.CharField(max_length=256)
    description = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=[("LOOKING", "Actively Looking"), ("OPEN", "Open to Offers"), ("BUSY", "Currently Busy")],
        default="OPEN",
    )

    salary_expectation = models.IntegerField(default=0)
    salary_cadence = models.CharField(max_length=10, choices=[("YEAR", "Year"), ("HOUR", "Hour")], default="YEAR")

    role = models.CharField(
        max_length=20,
        choices=[
            ("JUNIOR", "Junior"),
            ("MID", "Mid-Level"),
            ("SENIOR", "Senior"),
            ("PRINCIPAL", "Principal / staff"),
            ("CLEVEL", "C-Level"),
        ],
        default="MID",
    )

    # comma separated list (from multiple choice)
    capacity = models.CharField(
        max_length=100,
        choices=[
            ("PTC", "Part-time Contractor"),
            ("FTC", "Full-time Contractor"),
            ("PTE", "Part-time Employee"),
            ("FTE", "Full-time Employee"),
        ],
    )

    # Geo
    location = models.CharField(max_length=50)  # City, Country
    TIMEZONES = tuple(zip(pytz.all_timezones, pytz.all_timezones))
    timezone = models.CharField(max_length=32, choices=TIMEZONES, default="UTC")

    def __str__(self):
        return self.user.username

    def get_absolute_url(self):
        return reverse("developer", kwargs={"pk": self.id})
