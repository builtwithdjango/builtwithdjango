from django.contrib.sitemaps import Sitemap
from .models import Project

class ProjectSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.8

    def items(self):
        return Project.objects.filter(published=True)

    def lastmod(self, obj):
        return obj.date_added