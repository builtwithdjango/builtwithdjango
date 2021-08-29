from django.urls import path

from .views import PostDetailView, PostListView

urlpatterns = [
    path("", PostListView.as_view(), name="blog"),
    path("<slug:slug>", PostDetailView.as_view(), name="post"),
]
