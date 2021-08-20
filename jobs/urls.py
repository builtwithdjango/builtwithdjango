from django.urls import path

from .views import JobCreateView, JobDetailView, JobListView, ThankYouView

urlpatterns = [
    path("", JobListView.as_view(), name="jobs"),
    path("<int:pk>", JobDetailView.as_view(), name="job_details"),
    path("new", JobCreateView.as_view(), name="post_job"),
    path("thank-you", ThankYouView.as_view(), name="job_thank_you"),
]
