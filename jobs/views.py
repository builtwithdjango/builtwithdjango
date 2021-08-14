from datetime import datetime, timedelta

from django.views.generic import ListView, DetailView

from .models import Job
from newsletter.views import NewsletterSignupForm


class JobListView(ListView):
    model = Job
    template_name = "jobs/all_jobs.html"
    filter_date = datetime.today() - timedelta(days=31)
    queryset = Job.objects.filter(created_datetime__gte=filter_date)

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
