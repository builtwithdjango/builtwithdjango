from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponseRedirect
from django.views.generic import TemplateView, CreateView
from django.urls import reverse_lazy
from django.conf import settings
from django.contrib import messages
from django.shortcuts import render
import requests

from .models import Emails
from .forms import NewsletterSignupForm


class NewsletterSignupView(SuccessMessageMixin, CreateView):
    template_name = "newsletter/email-form.html"
    form_class = NewsletterSignupForm
    model = Emails
    success_url = reverse_lazy("home")
    success_message = "Thanks for subscribing!"

    def form_valid(self, form):
        self.object = form.save()

        emailoctopus_api_key = settings.EMAILOCTOPUS_API
        list_id = settings.OCTO_LIST_ID

        data = {
            "api_key": emailoctopus_api_key,
            "email_address": self.object.user_email,
        }

        r = requests.post(
            f"https://emailoctopus.com/api/1.5/lists/{list_id}/contacts", data=data
        )
        messages.success(self.request, "Thanks for subscribing!")

        return HttpResponseRedirect(reverse_lazy("home"))


class NewsletterThanksView(TemplateView):
    template_name = "newsletter/sucessfull-email-submit.html"
