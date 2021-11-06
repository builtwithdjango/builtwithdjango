from django.conf import settings
from django.db import models
from django.urls import reverse


class Maker(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    # Basic Info
    first_name = models.CharField(max_length=20, blank=True)
    last_name = models.CharField(max_length=20, blank=True)
    maker_email = models.EmailField(blank=True)
    maker_profile_image = models.ImageField(
        upload_to="maker_profile_image/", blank=True
    )
    # https://learndjango.com/tutorials/django-slug-tutorial
    slug = models.SlugField(null=True, unique=True)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="maker",
    )

    # Social
    twitter_handle = models.CharField(max_length=20, blank=True)
    github_handle = models.CharField(max_length=20, blank=True)
    indiehackers = models.CharField(max_length=20, blank=True)
    personal_website = models.URLField(blank=True)

    # Additional
    interviewed = models.BooleanField(default=False)
    short_bio = models.TextField(blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def get_absolute_url(self):
        return reverse("maker", kwargs={"slug": self.slug})
