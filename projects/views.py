from django.views.generic import ListView, DetailView, CreateView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy

from newsletter.views import NewsletterSignupForm
from .models import Project, Maker
from .forms import AddProject

from rest_framework import generics
from rest_framework.pagination import PageNumberPagination
from .serializers import ProjectsSerializer, MakersSerializer


class ProjectListView(ListView):
    model = Project
    template_name = "home.html"
    queryset = Project.objects.filter(published=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["newsletter_form"] = NewsletterSignupForm

        return context


class ProjectDetailView(DetailView):
    model = Project
    template_name = "projects/project_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["newsletter_form"] = NewsletterSignupForm

        return context


class ProjectCreateView(SuccessMessageMixin, CreateView):
    model = Project
    form_class = AddProject
    template_name = "submit-project.html"
    success_url = reverse_lazy("home")
    success_message = """
        Thanks for submitting your project! I'll let you know when it is up on the site!
    """
