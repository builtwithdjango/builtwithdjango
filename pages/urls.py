from django.urls import path

from .views import DonateOneTimeView, DonateSubscriptionView, HomeView

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("support/", DonateOneTimeView.as_view(), name="support"),
    path(
        "support-subscription/",
        DonateSubscriptionView.as_view(),
        name="support_subscription",
    ),
]
