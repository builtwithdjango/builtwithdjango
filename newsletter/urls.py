from django.urls import path

from .views import (
    NewsletterSignupView,
    NewsletterThanksView,
    getWeeklyTemplateView,
)

urlpatterns = [
    path("", NewsletterSignupView.as_view(), name="newsletter_home"),
    path(
        "email-signup-thanks/",
        NewsletterThanksView.as_view(),
        name="newsletter_thanks",
    ),
    path(
        "get-weekly-template/",
        getWeeklyTemplateView,
        name="get-weekly-template",
    ),
]
