import requests
from autoslug import AutoSlugField
from django.conf import settings
from django.db import models
from django.urls import reverse
from model_utils.models import TimeStampedModel

from builtwithdjango.utils import get_builtwithdjango_logger

logger = get_builtwithdjango_logger(__name__)


class Project(models.Model):
    """Model for a Project."""

    date_added = models.DateTimeField(auto_now_add=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    # Required Information
    title = models.CharField(max_length=100, unique=True)
    url = models.URLField(unique=True)
    short_description = models.CharField(max_length=200)
    user_email = models.EmailField(blank=True, null=True)
    slug = AutoSlugField(populate_from="title", always_update=True)
    published = models.BooleanField(default=False)
    large_company = models.BooleanField(default=False)
    type = models.CharField(max_length=50, blank=True)
    is_profitable = models.BooleanField(default=False)
    active = models.BooleanField(default=True)

    # Optional Website Information
    is_open_source = models.BooleanField(default=False)
    description = models.TextField(blank=True)
    homepage_screenshot = models.ImageField(upload_to="website_homepage_screenshot/", blank=True)
    twitter_url = models.URLField(blank=True)
    github_url = models.URLField(blank=True)

    logged_in_maker = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="project", blank=True, null=True
    )

    technologies = models.ManyToManyField("Technology", related_name="projects", blank=True)

    ### Ideally I would automatically parse suggestions, but
    ### Will have to manually add those technologies :shrug
    technology_suggestions_by_user = models.TextField(blank=True)

    is_for_sale = models.BooleanField(default=False)
    sponsored = models.BooleanField(default=False)
    sale_link = models.URLField(blank=True)

    # To remove
    additional_info = models.TextField(blank=True)
    requirements = models.TextField(blank=True)
    maker = models.ForeignKey(
        "makers.Maker",
        related_name="projects",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    # AI Augmented Fields
    date_scraped = models.DateTimeField(blank=True, null=True)
    page_content_markdown = models.TextField(blank=True)
    page_title = models.CharField(max_length=200, blank=True)
    page_description = models.TextField(blank=True)
    page_content_html = models.TextField(blank=True)

    audience_analysis = models.JSONField(blank=True, null=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("project", kwargs={"slug": self.slug})

    def check_project_is_active(self):
        try:
            response = requests.get(self.url, timeout=7)
            self.active = response.status_code == 200
        except (requests.RequestException, ConnectionError, requests.exceptions.ConnectTimeout) as e:
            logger.error(f"check_project_is_active error: {e}")
            self.active = False

        return self.active

    class Meta:
        ordering = ["-date_added"]


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

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="comments")
    comment = models.TextField(max_length=240)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        ordering = ("-created_date",)

    def __str__(self):
        return self.comment

    def get_absolute_url(self):
        return reverse("project", args=[self.project.slug])


class Like(TimeStampedModel):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="like")
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="like")
    like = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.project}: {self.author} ({self.like})"
