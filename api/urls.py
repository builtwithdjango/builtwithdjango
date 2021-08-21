from django.urls import path

from .views import CreateLikeProjectAPIView, UpdateLikeProjectAPIView

urlpatterns = [
    path("like/", CreateLikeProjectAPIView.as_view()),
    path("like/<int:pk>/", UpdateLikeProjectAPIView.as_view()),
]
