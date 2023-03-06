from django.views.generic import ListView

from .models import Developer


class DeveloperListView(ListView):
    model = Developer
    template_name = "developers/all_developers.html"
