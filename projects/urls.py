from django.urls import path
from .views import (
    ProjectListView, 
    ProjectDetailView, 
    ProjectCreateView,
    ProjectsAPIView,
    MakersAPIView
)

urlpatterns = [
    path("", ProjectListView.as_view(), name="home"),
    path("<slug:slug>", ProjectDetailView.as_view(), name="project"),
    path("project/new/", ProjectCreateView.as_view(), name="submit-project"),

    path('projects-list/', ProjectsAPIView.as_view(), name='projects-json'),
    path('makers-list/', MakersAPIView.as_view(), name='makers-json'),
]
