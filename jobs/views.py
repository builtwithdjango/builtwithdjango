from datetime import timedelta
from functools import partial

import stripe
from django.db import transaction
from django.shortcuts import redirect
from django.templatetags.static import static
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.html import escape
from django.views.generic import CreateView, DetailView, ListView, TemplateView
from django_q.tasks import async_task
from djstripe import models, settings as djstripe_settings

from newsletter.views import NewsletterSignupForm

from .forms import PostJob
from .models import Job
from .tasks import notify_of_new_job

stripe.api_key = djstripe_settings.djstripe_settings.STRIPE_SECRET_KEY


class AllJobListView(ListView):
    model = Job
    template_name = "jobs/all_jobs.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["newsletter_form"] = NewsletterSignupForm

        return context


class JobListView(ListView):
    model = Job
    template_name = "jobs/all_jobs.html"
    filter_date = timezone.now() - timedelta(days=60)
    queryset = Job.objects.filter(approved=True, created_datetime__gte=filter_date).order_by(
        "-paid", "-created_datetime"
    )[:30]

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

        job = self.object
        title = f"{job.company.name if job.company else job.company_name}"
        description = job.title

        # Ensure the company_logo URL is absolute
        if job.company_logo:
            image_url = self.request.build_absolute_uri(job.company_logo.url)
        else:
            # Fallback to a default image if no company logo is available
            image_url = self.request.build_absolute_uri(static("vendors/images/logo.png"))

        og_image_url = (
            f"https://osig.app/g?"
            f"site=x&"
            f"title={title}&"
            f"subtitle={description}&"
            f"image_url={image_url}&"
            f"font=helvetica&"
            f"style=logo&"
            f"key=dQrmHqDSY5"
        )
        context["og_image"] = og_image_url

        return context


class JobCreateView(CreateView):
    model = Job
    form_class = PostJob
    template_name = "jobs/post-job.html"

    def get_success_url(self):
        return reverse("stripe_checkout_session", kwargs={"pk": self.object.id})

    def form_valid(self, form):
        form.instance.logged_in_maker = self.request.user
        self.object = form.save()
        async_task(notify_of_new_job, self.object)
        return super(JobCreateView, self).form_valid(form)


class ThankYouView(TemplateView):
    template_name = "jobs/post-job-thank-you.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["newsletter_form"] = NewsletterSignupForm

        return context


def create_checkout_session(request, pk):
    price_id = models.Price.objects.get(nickname="job").id

    checkout_session = stripe.checkout.Session.create(
        success_url=request.build_absolute_uri(reverse_lazy("job_thank_you")) + "?session_id={CHECKOUT_SESSION_ID}",
        cancel_url=request.build_absolute_uri(reverse_lazy("home")) + "?status=failed",
        mode="payment",
        line_items=[
            {
                "quantity": 1,
                "price": price_id,
            }
        ],
        allow_promotion_codes=True,
        automatic_tax={"enabled": True},
        metadata={"pk": pk, "price_id": price_id},
    )

    return redirect(checkout_session.url, code=303)


def process_job_webhook(event):
    if event.type == "checkout.session.completed":
        transaction.on_commit(partial(update_job_to_paid, event))


def update_job_to_paid(event):
    job_id = event.data["object"]["metadata"]["pk"]
    job = Job.objects.get(pk=job_id)
    job.paid = True
    job.approved = True
    job.save()
