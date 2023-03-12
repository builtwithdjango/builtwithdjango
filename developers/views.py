import logging
from functools import partial

import stripe
from allauth.account.models import EmailAddress
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView, UpdateView
from djstripe import models, settings as djstripe_settings, webhooks

from users.models import CustomUser

from .forms import UpdateDeveloperForm
from .models import Developer

logger = logging.getLogger(__file__)
stripe.api_key = djstripe_settings.djstripe_settings.STRIPE_SECRET_KEY


class DeveloperListView(ListView):
    model = Developer
    template_name = "developers/all_developers.html"
    queryset = Developer.objects.filter(looking_for_a_job=True)


class DeveloperUpdateView(UpdateView):
    model = Developer
    form_class = UpdateDeveloperForm
    template_name = "developers/create-profile.html"
    success_message = "Developer Profile Updated"
    success_url = reverse_lazy("update-profile")

    def get_initial(self):
        initial = super().get_initial()
        developer = Developer.objects.get(user=self.request.user)
        capacity = developer.capacity.split(",") if developer.capacity else []
        initial["custom_capacity_field"] = capacity
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user = self.request.user
        emailaddress = EmailAddress.objects.get_for_user(user, user.email)
        email_verified = emailaddress.verified
        developer, created = Developer.objects.get_or_create(user=user)

        context["email_verified"] = email_verified
        context["current_developer"] = developer

        return context

    def form_valid(self, form):
        form.instance.user = self.request.user

        capacity_choices = form.cleaned_data["custom_capacity_field"]
        capacity = ",".join(capacity_choices)
        form.instance.capacity = capacity

        logger.info(f"Form: {form}")

        self.object = form.save()

        return super(DeveloperUpdateView, self).form_valid(form)


class DeveloperDetailView(DetailView):
    model = Developer
    template_name = "developers/developer_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.object:
            context["developer_capacity"] = self.object.capacity.split(",")

        return context


def create_checkout_session(request):
    user = request.user
    price_id = models.Price.objects.get(nickname="django_devs").id
    customer = models.Customer.objects.get(subscriber=user)

    checkout_session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        customer=customer.id,
        line_items=[
            {
                "price": price_id,
                "quantity": 1,
            }
        ],
        mode="subscription",
        allow_promotion_codes=True,
        automatic_tax={"enabled": True},
        success_url=request.build_absolute_uri(reverse_lazy("update-profile")) + "?session_id={CHECKOUT_SESSION_ID}",
        cancel_url=request.build_absolute_uri(reverse_lazy("update-profile")) + "?status=failed",
        metadata={f"user_id": user.id, "price_id": price_id},
    )

    return redirect(checkout_session.url, code=303)


def process_django_devs_webhook(event):
    if event.type == "checkout.session.completed":
        subscription_id = event.data["object"]["subscription"]
        logger.info(f"Updating Subsctiprion ID: {subscription_id}")
        models.Subscription.sync_from_stripe_data(stripe.Subscription.retrieve(subscription_id))

        transaction.on_commit(partial(update_django_dev_subscription_flag, event))

    return HttpResponse(status=200)


def update_django_dev_subscription_flag(event):
    logger.info(f"update_django_dev_subscription_flag started")
    user_id = event.data["object"]["metadata"]["user_id"]
    user = CustomUser.objects.get(id=user_id)
    user.has_active_django_devs_subscription = True
    user.save()


def create_customer_portal_session(request):
    customer = models.Customer.objects.get(subscriber=request.user)
    session = stripe.billing_portal.Session.create(
        customer=customer.id,
        return_url=request.build_absolute_uri(reverse_lazy("update-profile")),
    )

    return redirect(session.url)
