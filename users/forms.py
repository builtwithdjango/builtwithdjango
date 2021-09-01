from django import forms
from django.contrib.auth.forms import (
    AuthenticationForm,
    UserChangeForm,
    UserCreationForm,
)
from django.core.mail import send_mail
from django.db import transaction

from .models import CustomUser
from .utils import DivErrorList


class CustomUserCreationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.error_class = DivErrorList

        self.fields["username"].widget.attrs.update(
            {
                "placeholder": "Username",
                "class": """
                relative block w-full px-3 py-2 text-gray-900 placeholder-gray-500
                border border-gray-300 rounded-none appearance-none rounded-t-md
                focus:outline-none focus:ring-green-500 focus:border-green-500 focus:z-10 sm:text-sm
            """,
            }
        )
        self.fields["email"].widget.attrs.update(
            {
                "placeholder": "Email",
                "class": """
                relative block w-full px-3 py-2 text-gray-900 placeholder-gray-500
                border border-gray-300 rounded-none appearance-none focus:outline-none
                focus:ring-green-500 focus:border-green-500 focus:z-10 sm:text-sm
            """,
            }
        )
        self.fields["password1"].widget.attrs.update(
            {
                "placeholder": "Password",
                "class": """
                relative block w-full px-3 py-2 text-gray-900 placeholder-gray-500
                border border-gray-300 rounded-none appearance-none focus:outline-none
                focus:ring-green-500 focus:border-green-500 focus:z-10 sm:text-sm
            """,
            }
        )
        self.fields["password2"].widget.attrs.update(
            {
                "placeholder": "Confirm Password",
                "class": """
                relative block w-full px-3 py-2 text-gray-900 placeholder-gray-500
                border border-gray-300 rounded-none appearance-none rounded-b-md
                focus:outline-none focus:ring-green-500 focus:border-green-500 focus:z-10 sm:text-sm
            """,
            }
        )

    def save(self):
        instance = super(CustomUserCreationForm, self).save()

        @transaction.on_commit
        def send_notification():
            message = f"""
            We have a new user.
            Instance: {instance}
          """
            send_mail(
                "New User",
                message,
                "rasul@builtwithdjango.com",
                ["rasul@builtwithdjango.com"],
                fail_silently=False,
            )

        return instance

    class Meta(UserCreationForm):
        model = CustomUser
        fields = (
            "username",
            "email",
        )


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = UserChangeForm.Meta.fields


class CustomLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.error_class = DivErrorList

        self.fields["username"].widget.attrs.update(
            {
                "id": "username",
                "name": "username",
                "type": "username",
                "autocomplete": "username",
                "required": "true",
                "placeholder": "Username",
                "class": """
          relative block w-full px-3 py-2 text-gray-900 placeholder-gray-500
          border border-gray-300 rounded-none appearance-none rounded-t-md
          focus:outline-none focus:ring-green-500 focus:border-green-500 focus:z-10 sm:text-sm
        """,
            }
        )
        self.fields["password"].widget.attrs.update(
            {
                "id": "password",
                "name": "password",
                "type": "password",
                "autocomplete": "current-password",
                "required": "true",
                "placeholder": "Password",
                "class": """
          relative block w-full px-3 py-2 text-gray-900 placeholder-gray-500
          border border-gray-300 rounded-none appearance-none rounded-b-md
          focus:outline-none focus:ring-green-500 focus:border-green-500 focus:z-10 sm:text-sm
        """,
            }
        )
