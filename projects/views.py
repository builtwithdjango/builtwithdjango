from django.views.generic import ListView
from .models import Project


class SiteListView(ListView):
    model = Project
    template_name = 'home.html'
