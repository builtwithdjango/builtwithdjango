from datetime import datetime, timedelta
from django.contrib import sitemaps
from django.urls import reverse
from django.contrib.sitemaps import GenericSitemap

from projects.models import Project
from jobs.models import Job
from podcast.models import Episode


class StaticViewSitemap(sitemaps.Sitemap):
    """Generate Sitemap for the site
    """

    priority = 0.5

    def items(self):
        """Identify items that will be in the Sitemap

        Returns:
            List: urlNames that will be in the Sitemap
        """
        return [
            "home",
            "submit-project",
            "donate-one-time",
            "donate-subscription",
            "projects",
            "podcast_episodes",
            "jobs",
            "job-thank-you",
            "post-job",
        ]

    def location(self, item):
        """Get location for each item in the Sitemap

        Args:
            item (str): Item from the items function

        Returns:
            str: Url for the sitemap item
        """
        return reverse(item)


sitemaps = {
    "static": StaticViewSitemap,
    "projects": GenericSitemap(
        {
            "queryset": Project.objects.filter(published=True),
            "date_field": "date_added",
        },
        priority=0.8,
    ),
    "jobs": GenericSitemap(
        {
            "queryset": Job.objects.filter(
                created_datetime__gte=datetime.today() - timedelta(days=31)
            ),
            "date_field": "created_datetime",
        },
        priority=0.8,
    ),
    "podcast": GenericSitemap(
        {"queryset": Episode.objects.all(), "date_field": "created_datetime",},
        priority=0.8,
    ),
}
