import pytz
from autoslug import AutoSlugField
from cloudinary.models import CloudinaryField
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    # Basic profile
    first_name = models.CharField(max_length=20, blank=True)
    last_name = models.CharField(max_length=20, blank=True)
    slug = AutoSlugField(populate_from="username", always_update=True, editable=True)
    profile_image = CloudinaryField(
        "Image",
        overwrite=True,
        resource_type="image",
        folder=f"user-profile-image-{settings.ENVIRONMENT}",
        blank=True,
        null=True,
    )

    # Social
    twitter_handle = models.CharField(max_length=20, blank=True)
    github_handle = models.CharField(max_length=20, blank=True)
    indiehackers_handle = models.CharField(max_length=20, blank=True)
    personal_website = models.URLField(blank=True)

    # Additional
    make_public = models.BooleanField(default=True)
    interviewed = models.BooleanField(default=False)
    referred_by = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="referee",
    )

    # Plans
    FREE = "FREE"
    PRO = "PRO"
    SUBSCRIPTION_LEVEL = [
        (FREE, "FREE"),
        (PRO, "PRO"),
    ]
    subscription_level = models.CharField(
        max_length=15,
        choices=SUBSCRIPTION_LEVEL,
        default=FREE,
    )
    has_active_django_devs_subscription = models.BooleanField(default=False)

    class Meta:
        db_table = "auth_user"
