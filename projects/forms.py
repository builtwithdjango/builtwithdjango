from django.core.mail import send_mail
from django.db import transaction
from django.forms import ModelForm

from .models import Comment, Project


class AddProject(ModelForm):
    def __init__(self, *args, **kwargs):
        super(AddProject, self).__init__(*args, **kwargs)

        for fieldname in [
            "title",
            "user_email",
            "short_description",
            "url",
        ]:
            self.fields[fieldname].help_text = None
            self.fields[fieldname].widget.attrs.update(
                {
                    "class": "block appearance-none w-full bg-white border border-grey-light \
                              hover:border-grey px-2 py-2 rounded shadow"
                }
            )

        self.fields["url"].widget.attrs.update(
            {"placeholder": "https://test.com"}
        )

    def save(self):
        instance = super(AddProject, self).save()

        @transaction.on_commit
        def send_notification():
            message = f"""
            {instance.email} submitted a project.
            Instance: {instance}
          """
            send_mail(
                "New Project Submission",
                message,
                "rasul@builtwithdjango.com",
                ["rasul@builtwithdjango.com"],
                fail_silently=False,
            )

        return instance

    class Meta:
        model = Project
        fields = [
            "title",
            "user_email",
            "short_description",
            "url",
        ]


class AddComment(ModelForm):
    def __init__(self, *args, **kwargs):
        super(AddComment, self).__init__(*args, **kwargs)

        for fieldname in ["comment"]:
            self.fields[fieldname].help_text = None
            self.fields[fieldname].widget.attrs.update(
                {
                    "class": "block border w-full p-2 mb-2 border-gray-300 rounded-md \
                              shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm",
                    "rows": "3",
                }
            )

    class Meta:
        model = Comment
        fields = [
            "comment",
        ]
