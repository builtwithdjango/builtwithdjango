from django.urls import path

from .views import ProfileUpdateForm

urlpatterns = [
    path("update/", ProfileUpdateForm.as_view(), name="update-profile"),
    # path("signup/", SignUpView.as_view(), name="signup"),
    # path("login/", CustomLoginView.as_view(), name="login"),
]
