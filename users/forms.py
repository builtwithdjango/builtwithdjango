from django import forms
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.core.mail import send_mail
from django.db import transaction

from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):
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
