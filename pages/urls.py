from django.urls import path
from .views import HomeView, DonateOneTimeView, DonateSubscriptionView

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("support/", DonateOneTimeView.as_view(), name="support"),
    path(
        "donate-subscription/",
        DonateSubscriptionView.as_view(),
        name="donate-subscription",
    ),
]
