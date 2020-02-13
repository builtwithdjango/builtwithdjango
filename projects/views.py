from django.views.generic import ListView, DetailView, TemplateView
from django.views.generic.edit import CreateView
from django.contrib.messages.views import SuccessMessageMixin
from .models import Project
from django.urls import reverse_lazy
from .forms import AddProject


class ProjectListView(ListView):
    model = Project
    template_name = 'home.html'
    ordering = ['-date_added']
    
class ProjectCreateView(SuccessMessageMixin, CreateView):
    model = Project
    form_class = AddProject
    template_name = 'submit-project.html'
    success_url = reverse_lazy('home')
    success_message = "Thanks for submitting your project! I'll let you know when it is up on the site!"


class Thanks(TemplateView):
    template_name = "sucessfull-submit.html"