from autoslug import AutoSlugField
from cloudinary.models import CloudinaryField
from django.conf import settings
from django.db import models
from django.urls import reverse


class Job(models.Model):
    created_datetime = models.DateTimeField(auto_now_add=True)
    updated_datetime = models.DateTimeField(auto_now=True)

    submitted_datetime = models.DateTimeField(blank=True, null=True)
    source = models.CharField(max_length=100, blank=True)
    external_id = models.CharField(max_length=100, blank=True)

    title = models.CharField(max_length=100)
    slug = AutoSlugField(populate_from="title", always_update=True, default="django-developer")
    listing_url = models.URLField(unique=True)
    description = models.TextField(blank=True, null=True)
    email = models.EmailField(blank=True)
    min_yearly_salary = models.IntegerField(blank=True, null=True)
    max_yearly_salary = models.IntegerField(blank=True, null=True)

    remote = models.BooleanField(default=False)
    time_zone = models.CharField(max_length=100, blank=True)
    location = models.CharField(max_length=500, blank=True)

    company = models.ForeignKey(
        "Company",
        on_delete=models.CASCADE,
        related_name="jobs",
        blank=True,
        null=True,
    )

    # User Submitted
    company_name = models.CharField(max_length=100, blank=True)
    company_logo = CloudinaryField(
        "Image",
        overwrite=True,
        resource_type="image",
        folder=f"user-profile-image-{settings.ENVIRONMENT}",
        blank=True,
        null=True,
    )

    approved = models.BooleanField(default=False)
    paid = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_datetime"]

    def __str__(self):
        return f"{self.company_name} - {self.title} - {self.approved}"

    def get_absolute_url(self):
        return reverse("job_details", kwargs={"pk": self.id, "slug": self.slug})


class Company(models.Model):
    created_datetime = models.DateTimeField(auto_now_add=True)
    updated_datetime = models.DateTimeField(auto_now=True)

    name = models.CharField(max_length=100, unique=True)
    url = models.URLField(unique=True)
    slug = models.SlugField(null=True)
    logo = models.ImageField(upload_to="company_logo/")
    email = models.EmailField(blank=True)

    project = models.OneToOneField("projects.Project", on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name}"
