from django.forms import ModelForm
from .models import Project, Comment


class AddProject(ModelForm):
    def __init__(self, *args, **kwargs):
        super(AddProject, self).__init__(*args, **kwargs)

        for fieldname in [
            "website_title",
            "user_email",
            "website_short_description",
            "website_url",
        ]:
            self.fields[fieldname].help_text = None
            self.fields[fieldname].widget.attrs.update(
                {
                    "class": "block appearance-none w-full bg-white border border-grey-light hover:border-grey px-2 py-2 rounded shadow"
                }
            )

    class Meta:
        model = Project
        fields = [
            "website_title",
            "user_email",
            "website_short_description",
            "website_url",
        ]


class AddComment(ModelForm):
    def __init__(self, *args, **kwargs):
        super(AddComment, self).__init__(*args, **kwargs)

        for fieldname in ["comment"]:
            self.fields[fieldname].help_text = None
            self.fields[fieldname].widget.attrs.update(
                {
                    "class": "block border w-full p-2 mb-2 border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm",
                    "rows": "3",
                }
            )

    class Meta:
        model = Comment
        fields = [
            "comment",
        ]
