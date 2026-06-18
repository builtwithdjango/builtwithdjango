from django.urls import path

from . import views
from .views import (
    BlogPostListCreateAPIView,
    BlogPostRetrieveUpdateDestroyAPIView,
    CreateLikeProjectAPIView,
    ProjectLikeToggleAPIView,
    UpdateLikeProjectAPIView,
)

urlpatterns = [
    path("like/", CreateLikeProjectAPIView.as_view()),
    path("like/<int:pk>/", UpdateLikeProjectAPIView.as_view()),
    path("projects/<int:project_id>/like/", ProjectLikeToggleAPIView.as_view(), name="api_project_like_toggle"),
    path("search/projects/", views.search_projects, name="api_search_projects"),
    path("posts/", BlogPostListCreateAPIView.as_view(), name="api_create_post"),
    path("posts/<int:pk>/", BlogPostRetrieveUpdateDestroyAPIView.as_view(), name="api_post_detail"),
]
