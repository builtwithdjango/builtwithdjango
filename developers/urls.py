from django.urls import path

from .views import DeveloperListView

urlpatterns = [
    path("", DeveloperListView.as_view(), name="developers"),
]
