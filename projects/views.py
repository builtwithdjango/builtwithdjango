from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView
from .models import Project
from django.urls import reverse_lazy


class ProjectListView(ListView):
    model = Project
    template_name = 'home.html'


class ProjectCreateView(CreateView):
    model = Project
    template_name = 'submit_project.html'
    fields = '__all__'
    success_url = reverse_lazy('home')