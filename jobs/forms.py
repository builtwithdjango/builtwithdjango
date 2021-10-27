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
            "location",
            "salary",
            "company",
        ]:
            self.fields[fieldname].help_text = None
            self.fields[fieldname].widget.attrs.update(
                {
                    "class": "block appearance-none w-full bg-white border border-solid border-grey-light hover:border-grey px-2 py-2 rounded shadow"
                }
            )

    def save(self):
        instance = super(PostJob, self).save()

        @transaction.on_commit
        def send_notification():
            message = f"""
            Someone submitted a new job.
            Instance: {instance}
          """
            send_mail(
                "New Job Submission",
                message,
                "rasul@builtwithdjango.com",
                ["rasul@builtwithdjango.com"],
                fail_silently=False,
            )

        return instance

    class Meta:
        model = Job
        fields = ["title", "listing_url", "location", "salary", "company"]
