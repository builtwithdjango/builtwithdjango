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
    referred_by_username = forms.CharField()

    def __init__(self, *args, **kwargs):
        super(CustomUserUpdateForm, self).__init__(*args, **kwargs)

        self.fields["referred_by_username"].widget.attrs.update(
            {
                "class": "shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md",
            }
        )

    class Meta:
        model = get_user_model()
        fields = (
            "first_name",
            "last_name",
            "profile_image",
            "referred_by",
        )
        widgets = {"profile_image": ImageWidget}


class CustomLoginForm(LoginForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.error_class = DivErrorList

        self.fields["login"].widget.attrs.update(
            {
                "placeholder": "Username",
                "class": """
                    relative block w-full px-3 py-2 text-gray-900 placeholder-gray-500
                    border border-solid border-gray-300 rounded-none appearance-none rounded-t-md
                    focus:outline-none focus:ring-green-500 focus:border-green-500 focus:z-10 sm:text-sm
                """,
            }
        )
        self.fields["password"].widget.attrs.update(
            {
                "placeholder": "Password",
                "class": """
                    relative block w-full px-3 py-2 text-gray-900 placeholder-gray-500
                    border border-solid border-gray-300 rounded-none appearance-none rounded-b-md
                    focus:outline-none focus:ring-green-500 focus:border-green-500 focus:z-10 sm:text-sm
                """,
            }
        )

    # def login(self, *args, **kwargs):
    #     # You must return the original result.
    #     return super(CustomLoginForm, self).login(*args, **kwargs)
