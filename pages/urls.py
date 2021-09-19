from django.urls import path

from .views import (
    ConfirmEmail,
    DonateOneTimeView,
    DonateSubscriptionView,
    HomeView,
    RequestNftView,
)

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("support/", DonateOneTimeView.as_view(), name="support"),
    path("request-nft/", RequestNftView.as_view(), name="request-nft"),
    path(
        "confirm-nft-email/<slug:slug>",
        ConfirmEmail.as_view(),
        name="confirm-nft-email",
    ),
    path(
        "support-subscription/",
        DonateSubscriptionView.as_view(),
        name="support_subscription",
    ),
]
