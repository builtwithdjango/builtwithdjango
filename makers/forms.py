from django.forms import ModelForm

from .models import Maker


class ClaimAccountForm(ModelForm):
    class Meta:
        model = Maker
        fields = ("user",)
