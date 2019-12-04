from django.db import models
from django.urls import reverse
from autoslug import AutoSlugField
from taggit.managers import TaggableManager

class Project(models.Model):
    website_title = models.CharField(max_length=100, unique=True)
    website_url = models.URLField(unique=True)
    website_description = models.TextField()
    user_email = models.EmailField()
    slug = AutoSlugField(populate_from='website_title')
    published = models.BooleanField(default=False)
    tags = TaggableManager(blank=True)
    
    website_homepage_screenshot = models.ImageField(upload_to='website_homepage_screenshot/', blank=True)
    website_twitter = models.URLField(blank=True)
    website_github = models.URLField(blank=True)
    website_additional_info = models.TextField(blank=True)
    
    author_name = models.CharField(max_length=100, blank=True)
    author_email = models.EmailField(blank=True)
    author_website = models.URLField(blank=True)
    author_twitter = models.CharField(max_length=50, blank=True)
    author_github = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return str(self.published) + ": " + self.website_title
    
    def get_absolute_url(self):
        return reverse('website_detail', args=[self.slug])




