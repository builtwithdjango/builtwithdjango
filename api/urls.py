from django.urls import path

from . import views
from .views import CreateLikeProjectAPIView, UpdateLikeProjectAPIView

urlpatterns = [
    path("like/", CreateLikeProjectAPIView.as_view()),
    path("like/<int:pk>/", UpdateLikeProjectAPIView.as_view()),
    path("search/projects/", views.search_projects, name="api_search_projects"),
]
