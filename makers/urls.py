from django.urls import path

from .views import ClaimAccountView, MakerListView

urlpatterns = [
    path("", MakerListView.as_view(), name="makers"),
    path(
        "claim-account/<int:pk>/",
        ClaimAccountView.as_view(),
        name="claim_account",
    ),
]
