from django.urls import path

from .feeds import BlogFeed
from .views import PostDetailView, PostListView

urlpatterns = [
    path("", PostListView.as_view(), name="blog"),
    path("<slug:slug>", PostDetailView.as_view(), name="post"),
    path("feed/rss", BlogFeed(), name="blog_feed"),
]
