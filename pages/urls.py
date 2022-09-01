from django.urls import path

from .views import ConfirmEmail, HomeView, RequestNftView, SupportRedirect, TermsOfService

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("support/", SupportRedirect.as_view(), name="support"),
    path("terms/", TermsOfService.as_view(), name="terms-of-service"),
    path("request-nft/", RequestNftView.as_view(), name="request-nft"),
    path(
        "confirm-nft-email/<slug:slug>",
        ConfirmEmail.as_view(),
        name="confirm-nft-email",
    ),
]
