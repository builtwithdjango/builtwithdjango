from django.urls import path

from .views import AdvertizeView, ConfirmEmail, HomeView, RequestNftView, Support, TermsOfService

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("support/", Support.as_view(), name="support"),
    path("advertize", AdvertizeView.as_view(), name="advertize"),
    path("terms/", TermsOfService.as_view(), name="terms-of-service"),
    path("request-nft/", RequestNftView.as_view(), name="request-nft"),
    path(
        "confirm-nft-email/<slug:slug>",
        ConfirmEmail.as_view(),
        name="confirm-nft-email",
    ),
]
