from django.urls import path
from .views import (
    ProjectListView,
    ProjectDetailView,
    ProjectCreateView,
    CommentCreateView,
    MakerListView,
)

urlpatterns = [
    path("", ProjectListView.as_view(), name="projects"),
    path("makers/", MakerListView.as_view(), name="makers"),
    path("<slug:slug>", ProjectDetailView.as_view(), name="project"),
    path(
        "<slug:slug>/create-comment",
        CommentCreateView.as_view(),
        name="project_comment",
    ),
    path("new/", ProjectCreateView.as_view(), name="submit-project"),
]
