from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    profile_image = models.ImageField(upload_to="user_profile_image/", blank=True)

    class Meta:
        db_table = "auth_user"
