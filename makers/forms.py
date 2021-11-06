from django import forms
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


class MakerUpdateViewForm(ModelForm):
    # maker_profile_image = forms.ImageField(required=False, widget=forms.FileInput)
    remove_photo = forms.BooleanField(required=False)

    def __init__(self, *args, **kwargs):
        super(MakerUpdateViewForm, self).__init__(*args, **kwargs)

        self.fields["short_bio"].help_text = None
        self.fields["short_bio"].widget.attrs.update(
            {
                "class": "block w-full max-w-lg border border-gray-300 rounded-md shadow-sm \
                          focus:ring-green-500 focus:border-green-500 sm:text-sm",
                "rows": 6,
            }
        )

        # self.fields['maker_profile_image'].help_text = None
        # self.fields['maker_profile_image'].widget.attrs.update(
        #     {"class": "text-transparent"}
        # )

    class Meta:
        model = Maker
        fields = ["maker_profile_image", "short_bio"]
