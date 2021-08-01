from django.urls import path
from .views import JobListView

urlpatterns = [
    path("", JobListView.as_view(), name="jobs"),
]
