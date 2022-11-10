import datetime as dt
import json
from secrets import compare_digest

import stripe
from allauth.account.models import EmailAddress
from allauth.account.utils import send_email_confirmation
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
from djstripe import settings as djstripe_settings
from djstripe.models import Customer

from newsletter.views import NewsletterSignupForm

from .forms import CustomLoginForm, CustomUserCreationForm, CustomUserUpdateForm
from .models import CustomUser
from .tasks import notify_of_new_user

stripe.api_key = djstripe_settings.djstripe_settings.STRIPE_SECRET_KEY


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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user = self.request.user
        emailaddress = EmailAddress.objects.get_for_user(user, user.email)
        email_verified = emailaddress.verified

        context["email_verified"] = email_verified

        return context


class ProfileUpgrade(LoginRequiredMixin, TemplateView):
    login_url = "account_login"
    template_name = "account/upgrade-account.html"


def create_checkout_session(request, pk):
    checkout_session = stripe.checkout.Session.create(
        customer_email=request.user.email,
        success_url=request.build_absolute_uri(reverse_lazy("update-profile")) + "?session_id={CHECKOUT_SESSION_ID}",
        cancel_url=request.build_absolute_uri(reverse_lazy("update-profile")) + "?status=failed",
        mode="payment",
        line_items=[
            {
                "quantity": 1,
                "price": settings.USER_UPGRADE_PRICE_ID,
            }
        ],
        automatic_tax={"enabled": True},
        metadata={"pk": pk},
    )

    return redirect(checkout_session.url, code=303)


@csrf_exempt
@require_POST
def webhook(request):
    payload = request.body
    sig_header = request.META["HTTP_STRIPE_SIGNATURE"]
    event = None

    print(f"Users Payload: {payload}")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, settings.USER_UPGRADE_WEBHOOK_SECRET)
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    if event.type == "checkout.session.completed":
        user_id = event["data"]["object"]["metadata"]["pk"]

        current_user = CustomUser.objects.get(pk=user_id)
        current_user.subscription_level = "PRO"
        current_user.save()

    return HttpResponse(status=200)


def resend_email_confirmation_email(request):
    user = request.user
    send_email_confirmation(request, user, user.email)

    return redirect("update-profile")
