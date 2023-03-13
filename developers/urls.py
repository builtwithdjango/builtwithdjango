from django.urls import path

from .views import (
    DeveloperDetailView,
    DeveloperListView,
    DeveloperPricingView,
    DeveloperUpdateView,
    create_checkout_session,
    create_customer_portal_session,
)

urlpatterns = [
    path("", DeveloperListView.as_view(), name="developers"),
    path("pricing", DeveloperPricingView.as_view(), name="developers-pricing"),
    path("<uuid:pk>", DeveloperDetailView.as_view(), name="developer"),
    path("<uuid:pk>/update", DeveloperUpdateView.as_view(), name="update_developer"),
    path("create-checkout-session/", create_checkout_session, name="checkout-django-devs"),
    path(
        "create-customer-portal-session/",
        create_customer_portal_session,
        name="create-customer-portal-session",
    ),
]
