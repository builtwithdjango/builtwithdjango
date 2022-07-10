from django.forms import ModelForm

from .models import Comment


class CreateCommentForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(CreateCommentForm, self).__init__(*args, **kwargs)

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
