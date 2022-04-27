from django.urls import path

from .views import EpisodeDetailView, EpisodeListView

urlpatterns = [
    path("", EpisodeListView.as_view(), name="podcast_episodes"),
    path("<slug:slug>", EpisodeDetailView.as_view(), name="episode_details"),
]
