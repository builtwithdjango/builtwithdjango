from django.core.mail import send_mail
from django.db import transaction
from django.forms import ModelForm

from .models import Job


class PostJob(ModelForm):
    def __init__(self, *args, **kwargs):
        super(PostJob, self).__init__(*args, **kwargs)

        for fieldname in [
            "title",
            "listing_url",
            "email",
            "min_yearly_salary",
            "max_yearly_salary",
            "company_name",
        ]:
            self.fields[fieldname].help_text = None
            self.fields[fieldname].widget.attrs.update(
                {
                    "class": "shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md"
                }
            )

    class Meta:
        model = Job
        fields = [
            "title",
            "listing_url",
            "email",
            "min_yearly_salary",
            "max_yearly_salary",
            "company_name",
        ]
