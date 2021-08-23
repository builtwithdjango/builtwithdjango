from autoslug import AutoSlugField
from django.conf import settings
from django.db import models
from django.urls import reverse
from model_utils.models import TimeStampedModel
from taggit.managers import TaggableManager


class Project(models.Model):
    """Model for a Project."""

    date_added = models.DateTimeField(auto_now_add=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    # Required Information
    title = models.CharField(max_length=100, unique=True)
    url = models.URLField(unique=True)
    short_description = models.CharField(max_length=200)
    user_email = models.EmailField()
    slug = AutoSlugField(populate_from="title", always_update=True)
    published = models.BooleanField(default=False)

    # Optional Website Information
    is_open_source = models.BooleanField(default=False)
    description = models.TextField(blank=True)
    homepage_screenshot = models.ImageField(
        upload_to="website_homepage_screenshot/", blank=True
    )
    twitter_url = models.URLField(blank=True)
    github_url = models.URLField(blank=True)

    maker = models.ForeignKey(
        "makers.Maker", on_delete=models.CASCADE, null=True, blank=True
    )
    technologies = models.ManyToManyField(
        "Technology", related_name="projects", blank=True
    )

    # To remove
    additional_info = models.TextField(blank=True)
    requirements = models.TextField(blank=True)
    tags = TaggableManager(blank=True)

    class Meta:
        ordering = ["-date_added"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("project", args=[self.slug])


class Technology(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    name = models.CharField(max_length=50)
    color = models.CharField(max_length=50)
    slug = models.SlugField(
        null=True,
        unique=True,
    )

    def __str__(self):
        return self.name


class Comment(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="comments"
    )
    comment = models.TextField(max_length=240)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )

    def __str__(self):
        return self.comment

    def get_absolute_url(self):
        return reverse("project", args=[self.project.slug])


class Like(TimeStampedModel):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="like"
    )
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="like"
    )
    like = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.project}: {self.author} ({self.like})"
