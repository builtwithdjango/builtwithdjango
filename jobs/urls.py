from django.urls import path

from .feeds import LatestJobsFeed
from .views import JobCreateView, JobDetailView, JobListView, ThankYouView, create_checkout_session

urlpatterns = [
    path("", JobListView.as_view(), name="jobs"),
    path("<int:pk>/<slug:slug>", JobDetailView.as_view(), name="job_details"),
    path("new", JobCreateView.as_view(), name="post_job"),
    path("thank-you", ThankYouView.as_view(), name="job_thank_you"),
    path("create-checkout-session/<int:pk>/", create_checkout_session, name="stripe_checkout_session"),
    path("feed/rss", LatestJobsFeed(), name="jobs_feed"),
]
