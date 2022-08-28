import datetime as dt
import json
from secrets import compare_digest

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.contrib.messages.views import SuccessMessageMixin
from django.db.transaction import atomic, non_atomic_requests
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, TemplateView, UpdateView
from django_q.tasks import async_task

from newsletter.views import NewsletterSignupForm

from .forms import CustomLoginForm, CustomUserCreationForm, CustomUserUpdateForm
from .models import CustomUser, PayPalTransaction
from .tasks import notify_of_new_user


class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy("login")
    template_name = "account/signup.html"

    def get_context_data(self, **kwargs):
        context = super(SignUpView, self).get_context_data(**kwargs)
        context["newsletter_form"] = NewsletterSignupForm

        return context

    def form_valid(self, form):
        self.object = form.save()
        async_task(notify_of_new_user, self.object)

        return super(SignUpView, self).form_valid(form)


class CustomLoginView(LoginView):
    form_class = CustomLoginForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["newsletter_form"] = NewsletterSignupForm

        return context


class ProfileUpdateForm(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    login_url = "account_login"
    form_class = CustomUserUpdateForm
    model = CustomUser
    slug_field = "username"
    slug_url_kwarg = "username"
    success_message = "User Profile Updated"
    success_url = reverse_lazy("update-profile")
    template_name = "account/profile-update.html"

    def get_object(self, queryset=None):
        return self.request.user


class ProfileUpgrade(LoginRequiredMixin, TemplateView):
    login_url = "account_login"
    template_name = "account/upgrade-account.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["PAYPAL_CLIENT_ID"] = settings.PAYPAL_CLIENT_ID
        context["PAYPAL_WEBHOOK_SECRET"] = settings.PAYPAL_WEBHOOK_SECRET

        return context


@require_POST
def complete_upgrade_transaction(request):
    given_token = request.headers.get("Paypal-Secret", "")
    if not compare_digest(given_token, settings.PAYPAL_WEBHOOK_SECRET):
        return HttpResponseForbidden(
            "Incorrect Paypal token",
            content_type="text/plain",
        )

    payload = json.loads(request.body)

    given_user = payload["user"]
    if not compare_digest(given_user, request.user.username):
        return HttpResponseForbidden(
            "Incorrect User",
            content_type="text/plain",
        )

    PayPalTransaction.objects.filter(created__lte=timezone.now() - dt.timedelta(days=7)).delete()

    PayPalTransaction.objects.create(
        created=timezone.now(),
        user=request.user,
        payload=payload,
    )

    current_user = request.user
    current_user.subscription_level = "PRO"
    current_user.save()

    messages.success(request, "Upgrade was successful!")

    return redirect("update-profile")
