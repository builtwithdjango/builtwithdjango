from datetime import datetime, timedelta

from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, TemplateView

from newsletter.views import NewsletterSignupForm

from .forms import PostJob
from .models import Job


class JobListView(ListView):
    model = Job
    template_name = "jobs/all_jobs.html"
    filter_date = datetime.today() - timedelta(days=31)
    # queryset = Job.objects.filter(created_datetime__gte=filter_date).filter(
    #     approved=True
    # )
    queryset = Job.objects.filter(approved=True).order_by("-created_datetime")[
        :30
    ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["newsletter_form"] = NewsletterSignupForm

        return context


class JobDetailView(DetailView):
    model = Job
    template_name = "jobs/job_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["newsletter_form"] = NewsletterSignupForm

        return context


class JobCreateView(CreateView):
    model = Job
    form_class = PostJob
    template_name = "jobs/post-job.html"
    success_url = reverse_lazy("job_thank_you")


class ThankYouView(TemplateView):
    template_name = "jobs/post-job-thank-you.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["newsletter_form"] = NewsletterSignupForm

        return context
