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
                    "class": "block appearance-none w-full bg-white border border-solid border-grey-light \
                              hover:border-grey px-2 py-2 rounded shadow"
                }
            )

        self.fields["url"].widget.attrs.update({"placeholder": "https://test.com"})

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
                    "class": "block border border-solid w-full p-2 mb-2 border-gray-300 rounded-md \
                              shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm",
                    "rows": "3",
                }
            )

    class Meta:
        model = Comment
        fields = [
            "comment",
        ]


class ProjectUpdateViewForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(ProjectUpdateViewForm, self).__init__(*args, **kwargs)

        for fieldname in [
            "short_description",
            "twitter_url",
            "github_url",
            "sale_link",
        ]:
            self.fields[fieldname].help_text = None
            self.fields[fieldname].widget.attrs.update(
                {
                    "class": "max-w-lg block w-full shadow-sm focus:ring-indigo-500 focus:border-indigo-500 \
                          sm:max-w-xs sm:text-sm border-gray-300 rounded-md"
                }
            )

        for fieldname in ["description", "technology_suggestions_by_user"]:
            self.fields[fieldname].help_text = None
            self.fields[fieldname].widget.attrs.update(
                {
                    "class": "block w-full max-w-lg border border-gray-300 rounded-md shadow-sm \
                          focus:ring-green-500 focus:border-green-500 sm:text-sm",
                    "rows": 6,
                }
            )

        self.fields["is_for_sale"].help_text = None
        self.fields["is_for_sale"].widget.attrs.update(
            {"class": "focus:ring-indigo-500 h-4 w-4 text-indigo-600 border-gray-300 rounded"}
        )

    class Meta:
        model = Project
        fields = [
            "short_description",
            "description",
            "twitter_url",
            "github_url",
            "technology_suggestions_by_user",
            "is_for_sale",
            "sale_link",
        ]
