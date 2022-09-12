from django.urls import path

from .views import ProfileUpdateForm, ProfileUpgrade, create_checkout_session, webhook

urlpatterns = [
    path("update/", ProfileUpdateForm.as_view(), name="update-profile"),
    path("upgrade/", ProfileUpgrade.as_view(), name="upgrade-profile"),
    path("create-checkout-session/<int:pk>/", create_checkout_session, name="user_upgrade_checkout_session"),
    path("webhook/", webhook, name="user_upgrade_webhook"),
    # path("signup/", SignUpView.as_view(), name="signup"),
    # path("login/", CustomLoginView.as_view(), name="login"),
]
