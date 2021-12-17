from django.urls import path

from . import views
from .views import JobCreateView, JobDetailView, JobListView, ThankYouView

urlpatterns = [
    path("", JobListView.as_view(), name="jobs"),
    path("<int:pk>/<slug:slug>", JobDetailView.as_view(), name="job_details"),
    path("new", JobCreateView.as_view(), name="post_job"),
    path("thank-you", ThankYouView.as_view(), name="job_thank_you"),
    path("create-checkout-session/<int:pk>/", views.create_checkout_session, name="stripe_checkout_session"),
    path("webhook/", views.webhook, name="stripe_webhook"),
]
