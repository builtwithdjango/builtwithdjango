from django.urls import path

from .views import ProfileUpdateForm, ProfileUpgrade, accept_paddle_webhook, complete_upgrade_transaction

urlpatterns = [
    path("update/", ProfileUpdateForm.as_view(), name="update-profile"),
    path("upgrade/", ProfileUpgrade.as_view(), name="upgrade-profile"),
    path("upgrade-complete/", complete_upgrade_transaction, name="upgrade-complete"),
    path("paddle-webhook/8RUwjixXXaz4WjRn7BXCE2C7sns9easVS3u/", accept_paddle_webhook, name="paddle-user-webhook"),
    # path("signup/", SignUpView.as_view(), name="signup"),
    # path("login/", CustomLoginView.as_view(), name="login"),
]
