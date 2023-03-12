from django.forms import CheckboxSelectMultiple, ModelForm, MultipleChoiceField

from .models import Developer


class UpdateDeveloperForm(ModelForm):
    CAPACITY_CHOICES = [
        ("PTC", "Part-time Contractor"),
        ("FTC", "Full-time Contractor"),
        ("PTE", "Part-time Employee"),
        ("FTE", "Full-time Employee"),
    ]
    custom_capacity_field = MultipleChoiceField(choices=CAPACITY_CHOICES, widget=CheckboxSelectMultiple)

    def __init__(self, *args, **kwargs):
        super(UpdateDeveloperForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Developer
        fields = [
            "looking_for_a_job",
            "title",
            "description",
            "status",
            "role",
            "location",
            "timezone",
            "salary_expectation",
            "salary_cadence",
        ]
