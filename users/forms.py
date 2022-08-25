from allauth.account.forms import LoginForm
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserChangeForm, UserCreationForm
from django.core.mail import send_mail
from django.db import transaction
from django.forms.widgets import TextInput

from .models import CustomUser
from .utils import DivErrorList


class ImageWidget(forms.widgets.ClearableFileInput):
    template_name = "widgets/image_widget.html"


class CustomUserCreationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.error_class = DivErrorList

    class Meta:
        model = get_user_model()
        fields = ("username", "email", "password1", "password2")


class CustomUserUpdateForm(UserChangeForm):
    class Meta:
        model = get_user_model()
        fields = (
            "first_name",
            "last_name",
            "personal_website",
            "profile_image",
            "referred_by",
            "twitter_handle",
            "github_handle",
            "indiehackers_handle",
            "email",
            "make_public",
        )


class CustomLoginForm(LoginForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.error_class = DivErrorList
