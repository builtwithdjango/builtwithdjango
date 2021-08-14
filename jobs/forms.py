from django.forms import ModelForm
from .models import Job


class PostJob(ModelForm):
    def __init__(self, *args, **kwargs):
        super(PostJob, self).__init__(*args, **kwargs)

        for fieldname in ["title", "listing_url", "location", "salary", "company"]:
            self.fields[fieldname].help_text = None
            self.fields[fieldname].widget.attrs.update(
                {
                    "class": "block appearance-none w-full bg-white border border-grey-light hover:border-grey px-2 py-2 rounded shadow"
                }
            )

    class Meta:
        model = Job
        fields = ["title", "listing_url", "location", "salary", "company"]
