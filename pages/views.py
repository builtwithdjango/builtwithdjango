from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse, reverse_lazy
from django.views.generic import (
    CreateView,
    RedirectView,
    TemplateView,
    UpdateView,
)

from jobs.models import Job
from newsletter.views import NewsletterSignupForm
from podcast.models import Episode
from projects.models import Project

from .forms import AddNftRequest, ConfirmEmail
from .models import CistercianDateNftRequest


class HomeView(TemplateView):
    template_name = "pages/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["newsletter_form"] = NewsletterSignupForm
        context["projects"] = Project.objects.filter(published=True)[:6]
        context["podcast_episodes"] = Episode.objects.all()[:3]
        context["jobs"] = Job.objects.filter(approved=True).order_by(
            "-created_datetime"
        )[:6]

        return context


class SupportRedirect(RedirectView):
    url = "https://cryptip.to/builtwithdjango"


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
        Thanks for requesting an NFT. Before I mint it and send it to you, I will ask you one last thing.
        Can you please confirm your email? I just sent an email to your inbox with a link. Thanks a ton.
        Sorry for any inconvinience.
        If you would like to support this project, consider buying other NFTs from this collections :)
        Thanks!!!!
    """

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["dates_requested"] = CistercianDateNftRequest.objects.all()

        return context


class ConfirmEmail(SuccessMessageMixin, UpdateView):
    model = CistercianDateNftRequest
    form_class = ConfirmEmail
    template_name = "pages/confirm-email.html"
    success_url = reverse_lazy("request-nft")
    success_message = (
        "Thanks for confirming your email! You will receive your NFT shortly."
    )
    slug_field = "wallet_public_key"
