from django.urls import path

from .views import (
    CommentCreateView,
    CommentListView,
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
    path("<slug:slug>/comments", CommentListView.as_view(), name="list_project_comments"),
    path(
        "<slug:slug>/create-comment",
        CommentCreateView.as_view(),
        name="project_comment",
    ),
    path("new/", ProjectCreateView.as_view(), name="submit_project"),
]
