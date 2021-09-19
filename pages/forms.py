from django.core.mail import send_mail
from django.db import transaction
from django.forms import ModelForm

from .models import CistercianDateNftRequest


class AddNftRequest(ModelForm):
    def __init__(self, *args, **kwargs):
        super(AddNftRequest, self).__init__(*args, **kwargs)
        self.fields["email"].widget.attrs.update(
            {
                "class": "block w-full border-0 p-1 bg-gray-100 text-gray-900 placeholder-gray-500 focus:ring-0 sm:text-md",
                "placeholder": "test@example.com",
            }
        )
        self.fields["wallet_public_key"].widget.attrs.update(
            {
                "class": "block w-full border-0 p-1 bg-gray-100 text-gray-900 placeholder-gray-500 focus:ring-0 sm:text-md",
                "placeholder": "0x123456789651bE2ad266e9ca6A9d50686B183e49",
            }
        )
        self.fields["date_requested"].widget.attrs.update(
            {
                "class": "block w-full border-0 p-1 bg-gray-100 text-gray-900 placeholder-gray-500 focus:ring-0 sm:text-md",
                "placeholder": "2021-11-23",
            }
        )

    def save(self):
        instance = super(AddNftRequest, self).save()

        @transaction.on_commit
        def send_notification():
            message = f"""
            Hey,

            Please follow the link below to confirm your email. I did that to make sure people don't use fake identities.
            Thanks for understanding. I will send you the NFT right after you confirm.

            https://builtwithdjango.com/confirm-nft-email/{instance.wallet_public_key}
        """
            send_mail(
                "Please confirm your email :)",
                message,
                "rasul@builtwithdjango.com",
                [f"{instance.email}"],
                fail_silently=False,
            )

        return instance

    class Meta:
        model = CistercianDateNftRequest
        fields = ["email", "wallet_public_key", "date_requested"]


class ConfirmEmail(ModelForm):
    def __init__(self, *args, **kwargs):
        super(ConfirmEmail, self).__init__(*args, **kwargs)
        self.fields["email_confirmed"].widget.attrs.update({"checked": "true"})

    def save(self):
        instance = super(ConfirmEmail, self).save()

        @transaction.on_commit
        def send_notification():
            message = f"""
      {instance.email} just approved his NFT request.

      NFT INFO:
        - email: {instance.email}
        - wallet: {instance.wallet_public_key}
        - reqeusted date: {instance.date_requested}
            """
            send_mail(
                f"{instance.email} just approved his NFT request.",
                message,
                "rasul@builtwithdjango.com",
                ["rasul@builtwithdjango.com"],
                fail_silently=False,
            )

        return instance

    class Meta:
        model = CistercianDateNftRequest
        fields = ["email_confirmed"]
