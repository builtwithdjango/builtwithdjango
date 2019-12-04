from django.db import models
from django.urls import reverse
from autoslug import AutoSlugField

class Project(models.Model):
    website_url = models.URLField(unique=True)
    user_email = models.EmailField()
    website_title = models.CharField(max_length=100, unique=True)
    slug = AutoSlugField(populate_from='website_title')
    
    website_homepage_screenshot = models.ImageField(upload_to='website_homepage_screenshot/')
    website_description = models.TextField(blank=True)
    website_twitter = models.URLField(blank=True, unique=True)
    website_github = models.URLField(blank=True, unique=True)

    author_name = models.CharField(max_length=100)
    author_email = models.EmailField()
    author_twitter = models.URLField(blank=True)
    author_website = models.URLField(blank=True)

    def __str__(self):
        return self.website_title
    
    def get_absolute_url(self):
        return reverse('website_detail', args=[self.slug])




