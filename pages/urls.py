from django.urls import path

from .views import (
    AdminPanelView,
    AdvertizeView,
    ConfirmEmail,
    FetchJobsFromTJAlertsView,
    HomeView,
    RequestNftView,
    SendSponsorshipEmailView,
    Support,
    TermsOfService,
)

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
    path("admin-panel/", AdminPanelView.as_view(), name="admin-panel"),
    path("admin-panel/send-sponsorship-email/", SendSponsorshipEmailView.as_view(), name="send-sponsorship-email"),
    path(
        "admin-panel/fetch-jobs-from-tj-alerts/", FetchJobsFromTJAlertsView.as_view(), name="fetch-jobs-from-tj-alerts"
    ),
]
