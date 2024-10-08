from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.messages.views import SuccessMessageMixin
from django.templatetags.static import static  # Add this import
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, RedirectView, TemplateView, UpdateView

from blog.models import Post
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
        context["projects"] = Project.objects.filter(published=True, active=True).order_by("-sponsored", "-date_added")[
            :4
        ]
        context["guides"] = Post.objects.all()[:4]
        context["podcast_episodes"] = Episode.objects.all()[:3]
        context["jobs"] = Job.objects.filter(approved=True).order_by("-created_datetime")[:6]

        title = "Built with Django"
        description = "Learn to bring your project and business ideas to life with Django. Get inspired by others."
        logo_url = self.request.build_absolute_uri(static("vendors/images/logo.png"))
        og_image_url = (
            f"https://osig.app/g?"
            f"site=x&"
            f"title={title}&"
            f"subtitle={description}&"
            f"image_url={logo_url}&"
            f"font=markerfelt&"
            f"style=logo&"
            f"key=dQrmHqDSY5"
        )
        context["og_image"] = og_image_url

        return context


class AdvertizeView(TemplateView):
    template_name = "pages/advertize.html"


class Support(TemplateView):
    template_name = "pages/support.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["newsletter_form"] = NewsletterSignupForm

        return context


class DonateOneTimeView(TemplateView):
    template_name = "pages/support.html"

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
    success_message = "Thanks for confirming your email! You will receive your NFT shortly."
    slug_field = "wallet_public_key"


class TermsOfService(TemplateView):
    template_name = "pages/terms-of-service.html"
