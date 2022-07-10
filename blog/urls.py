from django.urls import path

from .feeds import BlogFeed
from .views import CommentCreateView, PostDetailView, PostListView

urlpatterns = [
    path("", PostListView.as_view(), name="blog"),
    path("<slug:slug>", PostDetailView.as_view(), name="post"),
    path(
        "<slug:slug>/create-comment",
        CommentCreateView.as_view(),
        name="create_guide_comment",
    ),
    path("feed/rss", BlogFeed(), name="blog_feed"),
]
