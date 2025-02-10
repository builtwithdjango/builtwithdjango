from django.urls import path

from .views import CreateLikeProjectAPIView, UpdateLikeProjectAPIView, search_projects

app_name = "api"

urlpatterns = [
    path("likes/", CreateLikeProjectAPIView.as_view(), name="likes"),
    path("likes/<int:pk>/", UpdateLikeProjectAPIView.as_view(), name="like-detail"),
    path("search/", search_projects, name="search"),
]
