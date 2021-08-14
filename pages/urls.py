from django.urls import path
from .views import HomeView, DonateOneTimeView, DonateSubscriptionView

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("donate-one-time/", DonateOneTimeView.as_view(), name="donate-one-time"),
    path(
        "donate-subscription/",
        DonateSubscriptionView.as_view(),
        name="donate-subscription",
    ),
]
