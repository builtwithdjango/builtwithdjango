from django.urls import path
from .views import JobListView, JobDetailView, JobCreateView, ThankYouView

urlpatterns = [
    path("", JobListView.as_view(), name="jobs"),
    path("<int:pk>", JobDetailView.as_view(), name="job_details"),
    path("new", JobCreateView.as_view(), name="post-job"),
    path("thank-you", ThankYouView.as_view(), name="job-thank-you"),
]
