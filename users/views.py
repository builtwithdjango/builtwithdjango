from functools import partial

import stripe
from allauth.account.adapter import get_adapter
from allauth.account.models import EmailAddress
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.contrib.messages.views import SuccessMessageMixin
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView, UpdateView
from djstripe import models, settings as djstripe_settings
from djstripe.event_handlers import djstripe_receiver

from builtwithdjango.utils import get_builtwithdjango_logger
from developers.forms import UpdateDeveloperForm
from developers.models import Developer
from developers.views import process_django_devs_webhook
from jobs.views import process_job_webhook
from newsletter.views import NewsletterSignupForm

from .forms import CustomUserUpdateForm
from .models import CustomUser

stripe.api_key = djstripe_settings.djstripe_settings.STRIPE_SECRET_KEY
logger = get_builtwithdjango_logger(__name__)


# Authentication is handled by Django Allauth
# See ACCOUNT_FORMS in settings.py for custom form configuration


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

    def get_initial(self):
        initial = super().get_initial()
        user = self.request.user
        developer, _ = Developer.objects.get_or_create(user=user)
        models.Customer.get_or_create(subscriber=user)
        initial["looking_for_a_job"] = developer.looking_for_a_job
        initial["title"] = developer.title
        initial["description"] = developer.description
        initial["status"] = developer.status
        initial["role"] = developer.role
        initial["location"] = developer.location
        initial["timezone"] = developer.timezone
        initial["salary_expectation"] = developer.salary_expectation
        initial["salary_cadence"] = developer.salary_cadence
        initial["custom_capacity_field"] = developer.capacity.split(",")
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user = self.request.user
        emailaddress = EmailAddress.objects.get_for_user(user, user.email)
        email_verified = emailaddress.verified
        developer, created = Developer.objects.get_or_create(user=user)

        context["email_verified"] = email_verified
        context["current_developer"] = developer
        context["developer_form"] = UpdateDeveloperForm(initial=self.get_initial())

        return context


class ProfileUpgrade(LoginRequiredMixin, TemplateView):
    login_url = "account_login"
    template_name = "account/upgrade-account.html"


def create_checkout_session(request, pk):
    user = request.user
    price_id = models.Price.objects.get(nickname="pro").id
    customer = models.Customer.objects.get(subscriber=user)

    checkout_session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        customer=customer.id,
        success_url=request.build_absolute_uri(reverse_lazy("update-profile")) + "?session_id={CHECKOUT_SESSION_ID}",
        cancel_url=request.build_absolute_uri(reverse_lazy("update-profile")) + "?status=failed",
        mode="payment",
        line_items=[
            {
                "quantity": 1,
                "price": price_id,
            }
        ],
        allow_promotion_codes=True,
        automatic_tax={"enabled": True},
        customer_update={
            "address": "auto",
        },
        metadata={"pk": pk, "price_id": price_id},
    )

    return redirect(checkout_session.url, code=303)


@djstripe_receiver("checkout.session.completed")
def successfull_payment_webhook(event, **kwargs):
    pro_price_id = models.Price.objects.get(nickname="pro").id
    devs_price_id = models.Price.objects.get(nickname="django_devs").id
    job_price_id = models.Price.objects.get(nickname="job").id

    event_price_id = event.data["object"]["metadata"]["price_id"]
    logger.info(f"Received webhook event for Price ID: {event_price_id}")

    if event_price_id == pro_price_id:
        logger.info("Processing PRO user purchase")
        process_pro_webhook(event)
    elif event_price_id == devs_price_id:
        logger.info("Processing Django Devs purchase")
        process_django_devs_webhook(event)
    elif event_price_id == job_price_id:
        logger.info("Processing Job Board purchase")
        process_job_webhook(event)
    else:
        logger.info("Not Processing this event")

    return HttpResponse(status=200)


def process_pro_webhook(event):
    if event.type == "checkout.session.completed":
        customer = event.data["object"]["customer"]
        logger.info(f"Upgrading Customer: {customer}")
        models.Customer.sync_from_stripe_data(stripe.Customer.retrieve(customer))

        transaction.on_commit(partial(update_user_to_pro, event))


def update_user_to_pro(event):
    user_id = event.data["object"]["metadata"]["pk"]

    current_user = CustomUser.objects.get(pk=user_id)
    current_user.subscription_level = "PRO"
    current_user.save()


def resend_email_confirmation_email(request):
    user = request.user
    adapter = get_adapter(request)
    emailaddress = EmailAddress.objects.get_for_user(user, user.email)
    adapter.send_confirmation_mail(request, emailaddress, signup=False)

    return redirect("update-profile")
