from django.db import models
from django.urls import reverse
from autoslug import AutoSlugField
from taggit.managers import TaggableManager


class Project(models.Model):
    # Required Information
    website_title = models.CharField(max_length=100, unique=True)
    website_url = models.URLField(unique=True)
    website_short_description = models.CharField(max_length=200)
    user_email = models.EmailField()
    slug = AutoSlugField(populate_from="website_title", always_update=True)
    published = models.BooleanField(default=False)
    date_added = models.DateTimeField(auto_now_add=True)
    tags = TaggableManager(blank=True)

    # Optional Website Information
    is_open_source = models.BooleanField(default=False)
    website_description = models.TextField(blank=True)
    website_homepage_screenshot = models.ImageField(
        upload_to="website_homepage_screenshot/", blank=True
    )
    website_twitter = models.URLField(blank=True)
    website_github = models.URLField(blank=True)
    website_additional_info = models.TextField(blank=True)
    website_requirements = models.TextField(blank=True)

    maker = models.ForeignKey("Maker", on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return (
            str(self.published)
            + ": "
            + self.website_title
            + " by "
            + str(self.maker)
            + " - "
            + str(self.date_added)
        )

    def get_absolute_url(self):
        return reverse("project", args=[self.slug])


class Maker(models.Model):
    # Basic Info
    first_name = models.CharField(max_length=20, blank=True)
    last_name = models.CharField(max_length=20, blank=True)
    maker_email = models.EmailField(blank=True)
    maker_profile_image = models.ImageField(
        upload_to="maker_profile_image/", blank=True
    )

    # Social
    twitter_handle = models.CharField(max_length=20, blank=True)
    github_handle = models.CharField(max_length=20, blank=True)
    indiehackers = models.CharField(max_length=20, blank=True)
    personal_website = models.URLField(blank=True)

    # Additional
    interviewed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
