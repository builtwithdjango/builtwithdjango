from django.urls import path

from .views import DeveloperDetailView, DeveloperListView, DeveloperUpdateView, create_checkout_session

urlpatterns = [
    path("", DeveloperListView.as_view(), name="developers"),
    path("<uuid:pk>", DeveloperDetailView.as_view(), name="developer"),
    path("<uuid:pk>/update", DeveloperUpdateView.as_view(), name="update_developer"),
    path("create-checkout-session/", create_checkout_session, name="checkout-django-devs"),
]
