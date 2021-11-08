from django.urls import path

from .views import (
    CommentCreateView,
    ProjectCreateView,
    ProjectDetailView,
    ProjectListView,
    ProjectUpdateView,
)

urlpatterns = [
    path("", ProjectListView.as_view(), name="projects"),
    path("<slug:slug>", ProjectDetailView.as_view(), name="project"),
    path(
        "<slug:slug>/update",
        ProjectUpdateView.as_view(),
        name="project_update",
    ),
    path(
        "<slug:slug>/create-comment",
        CommentCreateView.as_view(),
        name="project_comment",
    ),
    path("new/", ProjectCreateView.as_view(), name="submit_project"),
]
