import datetime as dt
import json
from secrets import compare_digest
from urllib import parse

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
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, TemplateView, UpdateView
from django_q.tasks import async_task

from newsletter.views import NewsletterSignupForm

from .forms import CustomLoginForm, CustomUserCreationForm, CustomUserUpdateForm
from .models import CustomUser, PaddleWebhook
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
        context["PADDLE_VENDOR_ID"] = settings.PADDLE_VENDOR_ID

        return context


def complete_upgrade_transaction(request):
    body = json.loads(request.body)
    print(f"BODY: {body}")

    current_user = request.user
    current_user.subscription_level = "PRO"
    current_user.save()

    messages.success(request, "Upgrade was successful!")

    return redirect("update-profile")


@csrf_exempt
@require_POST
@non_atomic_requests
def accept_paddle_webhook(request):
    given_token = request.headers.get("User-Agent", "")
    if not compare_digest(given_token, settings.PADDLE_USER_AGENT):
        return HttpResponseForbidden(
            "Incorrect User-Agent header.",
            content_type="text/plain",
        )

    PaddleWebhook.objects.filter(created__lte=timezone.now() - dt.timedelta(days=7)).delete()

    payload = parse.parse_qs(request.body.decode("utf-8"), keep_blank_values=True)

    if "alert_name" in payload.keys():
        alert_name = payload["alert_name"][0]
    else:
        alert_name = "pro_subscription"

    PaddleWebhook.objects.create(payload=payload, alert_name=alert_name)

    pretty = json.dumps(payload, indent=4, sort_keys=True)
    print(pretty)

    # process_webhook_payload(payload)

    return HttpResponse(content="You are now a PRO member", status=200)
