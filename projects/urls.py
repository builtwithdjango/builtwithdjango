from django.urls import path
from .views import (
    ProjectListView,
    ProjectDetailView,
    ProjectCreateView,
    CommentCreateView,
)

urlpatterns = [
    path("", ProjectListView.as_view(), name="home"),
    path("<slug:slug>", ProjectDetailView.as_view(), name="project"),
    path(
        "<slug:slug>/create-comment",
        CommentCreateView.as_view(),
        name="project_comment",
    ),
    path("project/new/", ProjectCreateView.as_view(), name="submit-project"),
]
