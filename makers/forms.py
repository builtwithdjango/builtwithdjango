from django.core.mail import send_mail
from django.db import transaction
from django.forms import ModelForm

from .models import Maker


class ClaimAccountForm(ModelForm):
    def save(self):
        instance = super(ClaimAccountForm, self).save()

        @transaction.on_commit
        def send_notification():
            message = f"""
          Someone tried claiming the account.
          Instance: {instance}
        """
            send_mail(
                "Account Claimed",
                message,
                "rasul@builtwithdjango.com",
                ["rasul@builtwithdjango.com"],
                fail_silently=False,
            )

        return instance

    class Meta:
        model = Maker
        fields = ("user",)
