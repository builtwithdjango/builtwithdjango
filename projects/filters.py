import django_filters

from .models import Project


class ProjectFilter(django_filters.FilterSet):
    def __init__(self, *args, **kwargs):
        super(ProjectFilter, self).__init__(*args, **kwargs)

    class Meta:
        model = Project
        fields = ["is_open_source"]
