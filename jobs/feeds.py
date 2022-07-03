from django.contrib.syndication.views import Feed
from django.template.defaultfilters import truncatewords

from .models import Job


class LatestJobsFeed(Feed):
    title = "Django Jobs"
    link = "https://builtwithdjango.com/jobs/"
    description = "Best Django jobs for best Django developers."

    def items(self):
        return Job.objects.filter(approved=True).order_by("-created_datetime")[:30]

    def item_title(self, item):
        return f"{item.title} at {item.company_name}"

    def item_description(self, item):
        return truncatewords(item.description, 50)
