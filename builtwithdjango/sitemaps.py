from django.contrib import sitemaps
from django.urls import reverse

class StaticViewSitemap(sitemaps.Sitemap):
    priority = 0.5

    def items(self):
        return ['home',
                'submit-project']

    def location(self, item):
        return reverse(item)