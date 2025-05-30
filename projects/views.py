from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Count, Q
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, UpdateView
from django_filters.views import FilterView
from django_q.tasks import async_task

from newsletter.forms import NewsletterSignupForm
from users.forms import CustomUserCreationForm

from .filters import ProjectFilter
from .forms import AddComment, AddProject, ProjectUpdateViewForm
from .hooks import screenshot_saved
from .models import Comment, Project
from .tasks import (
    fetch_page_content,
    notify_admins_of_comment,
    notify_of_new_project,
    notify_owner_of_new_comment,
    save_screenshot,
)


class ProjectListView(FilterView):
    model = Project
    template_name = "projects/all_projects.html"
    filterset_class = ProjectFilter
    paginate_by = 12

    def get_queryset(self):
        queryset = Project.objects.filter(published=True, active=True, might_be_spam=False).order_by(
            "-sponsored", "-updated_date"
        )

        if self.request.GET.get("order_by"):
            ordering = self.request.GET.get("order_by")

            if ordering == "like":
                queryset = (
                    queryset
                    # need like_count as an alias for comlex query
                    # https://stackoverflow.com/questions/39375339/django-complex-annotations-require-an-alias-what-is-alias-here
                    .annotate(like__count=Count("like", filter=Q(like__like=True))).order_by(
                        "-sponsored", f"-like__count"
                    )
                )
            elif ordering == "comments":
                queryset = queryset.annotate(Count(ordering)).order_by("-sponsored", f"-{ordering}__count")
            else:
                queryset = queryset.order_by("-sponsored", "-updated_date")

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["newsletter_form"] = NewsletterSignupForm

        return context


class InactiveProjectListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Project
    template_name = "projects/all_inactive_projects.html"
    queryset = Project.objects.filter(published=True, active=False, might_be_spam=False)

    def test_func(self):
        return self.request.user.is_staff


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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["registration_form"] = CustomUserCreationForm

        return context

    def form_valid(self, form):
        form.instance.logged_in_maker = self.request.user
        self.object = form.save()

        async_task(save_screenshot, self.object.title, hook=screenshot_saved)
        async_task(notify_of_new_project, self.object)
        async_task(fetch_page_content, self.object.id)

        return super(ProjectCreateView, self).form_valid(form)


class ProjectUpdateView(LoginRequiredMixin, UpdateView):
    login_url = "account_login"
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
        self.object = form.save()
        async_task(notify_owner_of_new_comment, self.object)
        async_task(notify_admins_of_comment, self.object)

        return super(CommentCreateView, self).form_valid(form)
