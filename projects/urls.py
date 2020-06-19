from django.urls import path
from .views import ProjectListView, ProjectDetailView, ProjectCreateView

urlpatterns = [
    path("", ProjectListView.as_view(), name="home"),
    path("<slug:slug>", ProjectDetailView.as_view(), name="project"),
    path("project/new/", ProjectCreateView.as_view(), name="submit-project"),
]
