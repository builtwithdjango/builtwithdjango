from autoslug import AutoSlugField
from cloudinary.models import CloudinaryField
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    first_name = models.CharField(max_length=20, blank=True)
    last_name = models.CharField(max_length=20, blank=True)
    slug = AutoSlugField(populate_from="username", always_update=True, editable=True)

    # Social
    twitter_handle = models.CharField(max_length=20, blank=True)
    github_handle = models.CharField(max_length=20, blank=True)
    indiehackers_handle = models.CharField(max_length=20, blank=True)
    personal_website = models.URLField(blank=True)

    # Additional
    interviewed = models.BooleanField(default=False)
    short_bio = models.TextField(blank=True)

    referred_by = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="referee",
    )
    profile_image = CloudinaryField(
        "Image",
        overwrite=True,
        resource_type="image",
        folder=f"user-profile-image-{settings.ENVIRONMENT}",
        blank=True,
        null=True,
    )

    class Meta:
        db_table = "auth_user"
