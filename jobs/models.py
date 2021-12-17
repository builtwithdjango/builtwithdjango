from autoslug import AutoSlugField
from django.db import models
from django.urls import reverse


class Job(models.Model):
    created_datetime = models.DateTimeField(auto_now_add=True)
    updated_datetime = models.DateTimeField(auto_now=True)

    title = models.CharField(max_length=100)
    slug = AutoSlugField(populate_from="title", always_update=True, default="django-developer")
    listing_url = models.URLField(unique=True)
    description = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    min_yearly_salary = models.IntegerField(blank=True, null=True)
    max_yearly_salary = models.IntegerField(blank=True, null=True)

    company = models.ForeignKey(
        "Company",
        on_delete=models.CASCADE,
        related_name="jobs",
        blank=True,
        null=True,
    )

    # User Submitted
    company_name = models.CharField(max_length=100, blank=True)

    approved = models.BooleanField(default=False)
    paid = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_datetime"]

    def __str__(self):
        return f"{self.company_name}: {self.title}"

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
