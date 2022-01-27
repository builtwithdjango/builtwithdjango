from autoslug import AutoSlugField
from cloudinary.models import CloudinaryField
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
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
        folder=f"user-profile-image-{settings.ENV}",
        blank=True,
        null=True,
    )

    class Meta:
        db_table = "auth_user"
