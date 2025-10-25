import stripe
from allauth.account.models import EmailAddress
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView, TemplateView, UpdateView
from djstripe import models, settings as djstripe_settings

from builtwithdjango.utils import get_builtwithdjango_logger

from .forms import UpdateDeveloperForm
from .models import Developer

logger = get_builtwithdjango_logger(__name__)
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


class DeveloperPricingView(LoginRequiredMixin, TemplateView):
    login_url = "account_login"
    template_name = "developers/pricing-details.html"


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
        customer_update={
            "address": "auto",
        },
        success_url=request.build_absolute_uri(reverse_lazy("update-profile")) + "?session_id={CHECKOUT_SESSION_ID}",
        cancel_url=request.build_absolute_uri(reverse_lazy("update-profile")) + "?status=failed",
        metadata={f"user_id": user.id, "price_id": price_id},
    )

    return redirect(checkout_session.url, code=303)


def create_customer_portal_session(request):
    customer = models.Customer.objects.get(subscriber=request.user)
    session = stripe.billing_portal.Session.create(
        customer=customer.id,
        return_url=request.build_absolute_uri(reverse_lazy("update-profile")),
    )

    return redirect(session.url)
