from django.urls import path

from .views import ProfileUpdateForm, ProfileUpgrade, create_checkout_session, resend_email_confirmation_email

urlpatterns = [
    path("update/", ProfileUpdateForm.as_view(), name="update-profile"),
    path("upgrade/", ProfileUpgrade.as_view(), name="upgrade-profile"),
    path("create-checkout-session/<int:pk>/", create_checkout_session, name="user_upgrade_checkout_session"),
    path("send-confirmation", resend_email_confirmation_email, name="resend_email_confirmation_email"),
    # Authentication handled by Django Allauth
]
