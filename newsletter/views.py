from datetime import datetime, timedelta

import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.contrib.messages.views import SuccessMessageMixin
from django.core.mail import send_mail
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView
from django_q.tasks import async_task

from jobs.models import Job
from podcast.models import Episode
from projects.models import Project

from .forms import NewsletterSignupForm, getWeeklyTemplateForm
from .models import Emails
from .tasks import add_email_to_buttondown


class NewsletterSignupView(SuccessMessageMixin, CreateView):
    template_name = "newsletter/email-form.html"
    form_class = NewsletterSignupForm
    model = Emails
    success_url = reverse_lazy("home")
    success_message = "Thanks for subscribing!"

    def form_valid(self, form):
        self.object = form.save()
        r_json = async_task(add_email_to_buttondown, self.object.user_email, tag="newsletter")

        messages.success(self.request, "Thanks for subscribing!")

        return HttpResponseRedirect(reverse_lazy("home"))


class NewsletterThanksView(TemplateView):
    template_name = "newsletter/sucessfull-email-submit.html"


@user_passes_test(lambda user: user.is_staff)
def getWeeklyTemplateView(request):
    form = getWeeklyTemplateForm(request.POST)
    if form.is_valid():
        days = form.cleaned_data["days"]
        filter_date = datetime.today() - timedelta(days=days)
        projects = Project.objects.filter(created_date__gte=filter_date).filter(published=True)
        jobs = Job.objects.filter(created_datetime__gte=filter_date).filter(approved=True)
        podcast_episodes = Episode.objects.filter(created_datetime__gte=filter_date)
        context = {
            "projects": projects,
            "jobs": jobs,
            "podcasts": podcast_episodes,
        }
        send_mail(
            "Weekly Email Template",
            render_to_string("newsletter/weekly-newsletter-template.md", context),
            "Built with Django <rasul@builtwithdjango.com>",
            ["Built with Django <rasul@builtwithdjango.com>"],
        )
        return redirect("home")
    return render(request, "newsletter/send-weekly-email.html", {"form": form})
