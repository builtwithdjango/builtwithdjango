from django.views.generic import ListView, DetailView, TemplateView
from django.views.generic.edit import CreateView
from .models import Project
from django.urls import reverse_lazy
from .forms import AddProject


class ProjectListView(ListView):
    model = Project
    template_name = 'home.html'
    ordering = ['-date_added']
    
class ProjectCreateView(CreateView):
    model = Project
    form_class = AddProject
    template_name = 'submit_project.html'
    success_url = reverse_lazy('sucessfull-submit')

class Thanks(TemplateView):
    template_name = "sucessfull-submit.html"