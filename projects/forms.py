from django.forms import ModelForm

from .models import Comment, Project


class AddProject(ModelForm):
    def __init__(self, *args, **kwargs):
        super(AddProject, self).__init__(*args, **kwargs)

    class Meta:
        model = Project
        fields = [
            "title",
            "short_description",
            "url",
            "twitter_url",
            "github_url",
            "technology_suggestions_by_user",
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
