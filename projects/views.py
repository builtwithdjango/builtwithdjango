from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from newsletter.views import NewsletterSignupForm

from .forms import AddComment, AddProject, ProjectUpdateViewForm
from .models import Comment, Project


class ProjectListView(ListView):
    model = Project
    template_name = "projects/all_projects.html"
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
        context["comment_form"] = AddComment

        return context


class ProjectCreateView(SuccessMessageMixin, CreateView):
    model = Project
    form_class = AddProject
    template_name = "projects/submit-project.html"
    success_url = reverse_lazy("projects")
    success_message = """
        Thanks for submitting your project! I'll let you know when it is up on the site!
    """


class ProjectUpdateView(LoginRequiredMixin, UpdateView):
    model = Project
    form_class = ProjectUpdateViewForm
    template_name = "projects/project_detail_update.html"
    success_message = "Project updated successfully!"

    def get_success_url(self):
        return reverse("project", kwargs={"slug": self.object.slug})


class CommentCreateView(CreateView):
    model = Comment
    form_class = AddComment
    template_name = "projects/submit-comment.html"

    def get_success_url(self):
        return reverse("project", kwargs={"slug": self.object.project.slug})

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.project = Project.objects.get(slug=self.kwargs["slug"])
        return super(CommentCreateView, self).form_valid(form)
