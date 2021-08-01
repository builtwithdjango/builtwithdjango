from django.db import models
from django.urls import reverse


class Job(models.Model):
    created_datetime = models.DateTimeField(auto_now_add=True)
    updated_datetime = models.DateTimeField(auto_now=True)

    job_title = models.CharField(max_length=100)
    job_listing_url = models.URLField(unique=True)
    job_location = models.CharField(max_length=100, blank=True)
    job_salary = models.IntegerField(blank=True, null=True)

    company = models.ForeignKey("Company", on_delete=models.CASCADE,)

    def __str__(self):
        return f"{self.company}: {self.job_title}"


class Company(models.Model):
    created_datetime = models.DateTimeField(auto_now_add=True)
    updated_datetime = models.DateTimeField(auto_now=True)

    company_name = models.CharField(max_length=100, unique=True)
    company_url = models.URLField(unique=True)
    company_logo = models.ImageField(upload_to="company_logo/")
    company_email = models.EmailField(blank=True)

    def __str__(self):
        return f"{self.company_name}"
