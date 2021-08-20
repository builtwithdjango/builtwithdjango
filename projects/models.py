from django.db import models
from django.urls import reverse
from django.contrib.auth import get_user_model
from autoslug import AutoSlugField
from taggit.managers import TaggableManager


class Project(models.Model):
    """Model for a Project."""

    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    # Required Information
    website_title = models.CharField(max_length=100, unique=True)
    website_url = models.URLField(unique=True)
    website_short_description = models.CharField(max_length=200)
    user_email = models.EmailField()
    slug = AutoSlugField(populate_from="website_title", always_update=True)
    published = models.BooleanField(default=False)
    date_added = models.DateTimeField(auto_now_add=True)

    # Optional Website Information
    tags = TaggableManager(blank=True)
    is_open_source = models.BooleanField(default=False)
    website_description = models.TextField(blank=True)
    website_homepage_screenshot = models.ImageField(
        upload_to="website_homepage_screenshot/", blank=True
    )
    website_twitter = models.URLField(blank=True)
    website_github = models.URLField(blank=True)
    website_additional_info = models.TextField(blank=True)
    website_requirements = models.TextField(blank=True)

    maker = models.ForeignKey(
        "makers.Maker", on_delete=models.CASCADE, null=True, blank=True
    )
    technologies = models.ManyToManyField(
        "Technology", related_name="projects", blank=True
    )

    class Meta:
        ordering = ["-date_added"]

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


class Technology(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    name = models.CharField(max_length=50)
    color = models.CharField(max_length=50)
    slug = models.SlugField(null=True, unique=True,)

    def __str__(self):
        return self.name


class Comment(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="comments"
    )
    comment = models.TextField(max_length=240)
    author = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)

    def __str__(self):
        return self.comment

    def get_absolute_url(self):
        return reverse("project", args=[self.project.slug])
