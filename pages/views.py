from datetime import datetime, timedelta

from django.conf import settings
from django.views.generic import TemplateView

from jobs.models import Job
from newsletter.views import NewsletterSignupForm
from podcast.models import Episode
from projects.models import Project


class HomeView(TemplateView):
    template_name = "pages/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["newsletter_form"] = NewsletterSignupForm
        context["projects"] = Project.objects.filter(published=True)[:6]
        context["podcast_episodes"] = Episode.objects.all()[:3]
        context["jobs"] = Job.objects.filter(
            created_datetime__gte=datetime.today() - timedelta(days=31)
        ).filter(approved=True)[:6]

        return context


class DonateOneTimeView(TemplateView):
    template_name = "pages/support.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["newsletter_form"] = NewsletterSignupForm
        context["PAYPAL_CLIENT_ID"] = settings.PAYPAL_CLIENT_ID

        return context


class DonateSubscriptionView(TemplateView):
    template_name = "pages/support-subscription.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["newsletter_form"] = NewsletterSignupForm

        return context
