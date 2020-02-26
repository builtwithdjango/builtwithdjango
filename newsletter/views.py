from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic import TemplateView, CreateView
from django.urls import reverse_lazy
from django.conf import settings
from django.contrib import messages
from django.shortcuts import render

from .models import Emails
from .forms import NewsletterSignupForm

class NewsletterSignupView(SuccessMessageMixin, CreateView):
    template_name = "newsletter/email-form.html"
    form_class = NewsletterSignupForm
    model = Emails
    success_url = reverse_lazy('home')
    success_message = "Thanks for subscribing!"

class NewsletterThanksView(TemplateView):
    template_name = "newsletter/sucessfull-email-submit.html"
