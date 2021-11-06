from django.urls import path

from .views import (
    ClaimAccountView,
    MakerDetailView,
    MakerListView,
    MakerUpdateView,
)

urlpatterns = [
    path("", MakerListView.as_view(), name="makers"),
    path("<slug:slug>", MakerDetailView.as_view(), name="maker"),
    path("<slug:slug>/update", MakerUpdateView.as_view(), name="maker_update"),
    path(
        "claim-account/<int:pk>/",
        ClaimAccountView.as_view(),
        name="claim_account",
    ),
]
