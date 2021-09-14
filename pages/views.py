from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView

from jobs.models import Job
from newsletter.views import NewsletterSignupForm
from podcast.models import Episode
from projects.models import Project

from .forms import AddNftRequest
from .models import CistercianDateNftRequest


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


class RequestNftView(SuccessMessageMixin, CreateView):
    model = CistercianDateNftRequest
    form_class = AddNftRequest
    template_name = "pages/request-nft.html"
    success_url = reverse_lazy("request-nft")
    success_message = """
        Thanks for requesting an NFT. I'll create it and send it to you at my earliest convinience.
        If you provided correct wallet address it should show up in your wallet soon.
        If you provided correct email I will let you know when I've sent it.
        If you would like to support this project, consider buying other NFTs from this collections :)
        Thanks!!!!
    """

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["dates_requested"] = CistercianDateNftRequest.objects.all()

        return context
