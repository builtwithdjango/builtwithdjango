from django.urls import path

from .views import ProfileUpdateForm, ProfileUpgrade, complete_upgrade_transaction

urlpatterns = [
    path("update/", ProfileUpdateForm.as_view(), name="update-profile"),
    path("upgrade/", ProfileUpgrade.as_view(), name="upgrade-profile"),
    path("upgrade-complete/", complete_upgrade_transaction, name="upgrade-complete"),
    # path("signup/", SignUpView.as_view(), name="signup"),
    # path("login/", CustomLoginView.as_view(), name="login"),
]
