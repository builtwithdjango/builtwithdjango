from datetime import datetime, timedelta

from allauth.account.models import EmailAddress
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponseRedirect
from django.templatetags.static import static  # Add this import
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import CreateView, RedirectView, TemplateView, UpdateView
from django_q.tasks import async_task

from blog.models import Post
from jobs.models import Job
from jobs.tasks import get_latest_jobs_from_tj_alerts, send_sponsorship_request_email
from newsletter.tasks import send_buttondown_newsletter
from newsletter.views import NewsletterSignupForm
from podcast.models import Episode
from projects.models import Project

from .forms import AddNftRequest, ConfirmEmail
from .models import CistercianDateNftRequest

User = get_user_model()


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


class AdminPanelView(UserPassesTestMixin, TemplateView):
    """Admin panel view - only accessible to superusers"""

    template_name = "pages/admin-panel.html"

    def test_func(self):
        """Only allow superusers to access this view"""
        return self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get statistics
        # Count confirmed users (users with verified email addresses)
        confirmed_users = (
            EmailAddress.objects.filter(verified=True).values_list("user_id", flat=True).distinct().count()
        )

        # Count total users
        total_users = User.objects.count()

        # Count published projects
        published_projects = Project.objects.filter(published=True).count()

        # Count total projects
        total_projects = Project.objects.count()

        # Get latest jobs (approved jobs)
        latest_jobs = Job.objects.filter(approved=True).order_by("-created_datetime")[:5]

        # Get the very latest job for sponsorship email
        latest_job = Job.objects.filter(approved=True).order_by("-created_datetime").first()

        context.update(
            {
                "confirmed_users_count": confirmed_users,
                "total_users_count": total_users,
                "published_projects_count": published_projects,
                "total_projects_count": total_projects,
                "latest_jobs": latest_jobs,
                "latest_job": latest_job,
            }
        )

        return context


class SendSponsorshipEmailView(UserPassesTestMixin, View):
    """View to trigger sponsorship email for the latest job"""

    def test_func(self):
        """Only allow superusers to access this view"""
        return self.request.user.is_superuser

    def post(self, request, *args, **kwargs):
        # Get the latest approved job
        latest_job = Job.objects.filter(approved=True).order_by("-created_datetime").first()

        if not latest_job:
            messages.error(request, "No approved jobs found to send sponsorship email.")
            return HttpResponseRedirect(reverse("admin-panel"))

        # Queue the async task
        async_task(send_sponsorship_request_email, latest_job, task_name=f"send_sponsorship_email_job_{latest_job.id}")

        messages.success(
            request, f"Sponsorship email task queued for job: {latest_job.title} at {latest_job.company_name}"
        )

        return HttpResponseRedirect(reverse("admin-panel"))


class FetchJobsFromTJAlertsView(UserPassesTestMixin, View):
    """View to trigger fetching latest jobs from TJ Alerts"""

    def test_func(self):
        """Only allow superusers to access this view"""
        return self.request.user.is_superuser

    def post(self, request, *args, **kwargs):
        # Queue the async task to fetch jobs
        async_task(get_latest_jobs_from_tj_alerts, task_name="fetch_jobs_from_tj_alerts")

        messages.success(request, "Job fetching task queued! New jobs from TJ Alerts will be imported shortly.")

        return HttpResponseRedirect(reverse("admin-panel"))


class PrepareNewsletterView(UserPassesTestMixin, View):
    """View to prepare and schedule newsletter with custom days_back parameter"""

    def test_func(self):
        """Only allow superusers to access this view"""
        return self.request.user.is_superuser

    def post(self, request, *args, **kwargs):
        # Get days_back from POST data, default to 7
        try:
            days_back = int(request.POST.get("days_back", 7))
            if days_back < 1 or days_back > 365:
                raise ValueError("Days must be between 1 and 365")
        except (ValueError, TypeError):
            messages.error(request, "Invalid number of days. Please enter a number between 1 and 365.")
            return HttpResponseRedirect(reverse("admin-panel"))

        # Queue the async task to prepare and send newsletter
        task_id = async_task(
            send_buttondown_newsletter, days_back=days_back, task_name=f"prepare_newsletter_{days_back}_days"
        )

        messages.success(
            request,
            f"Newsletter task queued successfully! Content from the last {days_back} days will be included. Task ID: {task_id}",
        )

        return HttpResponseRedirect(reverse("admin-panel"))
