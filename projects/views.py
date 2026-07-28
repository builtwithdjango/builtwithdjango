from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q
from django.templatetags.static import static
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, UpdateView
from django_filters.views import FilterView
from django_q.tasks import async_task

from builtwithdjango.analytics import capture
from newsletter.forms import NewsletterSignupForm

from .filters import ProjectFilter
from .forms import AddProject, ProjectUpdateViewForm
from .hooks import screenshot_saved
from .models import Project
from .querysets import with_like_metadata
from .tasks import fetch_page_content, notify_of_new_project, save_screenshot


class ProjectListView(FilterView):
    model = Project
    template_name = "projects/all_projects.html"
    filterset_class = ProjectFilter
    paginate_by = 12

    def get_queryset(self):
        queryset = with_like_metadata(
            Project.objects.filter(published=True, active=True, might_be_spam=False),
            getattr(self.request, "user", None),
        )

        if self.request.GET.get("order_by"):
            ordering = self.request.GET.get("order_by")

            if ordering == "like":
                return queryset.order_by("-sponsored", "-like_count")
            else:
                return queryset.order_by("-sponsored", "-updated_date")

        return queryset.order_by("-sponsored", "-updated_date")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["newsletter_form"] = NewsletterSignupForm
        context["canonical_path"] = reverse("projects")

        query_params = self.request.GET.copy()
        query_params.pop("page", None)
        if query_params:
            context["robots"] = "noindex,follow"
        elif context.get("page_obj") and context["page_obj"].number > 1:
            context["canonical_path"] = f"{reverse('projects')}?page={context['page_obj'].number}"

        return context


class InactiveProjectListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    login_url = "account_login"
    model = Project
    template_name = "projects/all_inactive_projects.html"

    def get_queryset(self):
        return with_like_metadata(
            Project.objects.filter(published=True, active=False, might_be_spam=False),
            self.request.user,
        )

    def test_func(self):
        return self.request.user.is_staff


class ProjectDetailView(DetailView):
    model = Project
    template_name = "projects/project_detail.html"

    def get_queryset(self):
        queryset = with_like_metadata(super().get_queryset(), self.request.user)
        if self.request.user.is_staff:
            return queryset

        public_queryset = queryset.filter(published=True, active=True, might_be_spam=False)
        if self.request.user.is_authenticated:
            return queryset.filter(
                Q(published=True, active=True, might_be_spam=False)
                | Q(logged_in_maker=self.request.user)
                | Q(maker__user=self.request.user)
            ).distinct()
        return public_queryset

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        capture(
            request,
            "project viewed",
            properties={
                "project_id": self.object.id,
                "project_title": self.object.title,
                "project_slug": self.object.slug,
                "project_type": self.object.type,
                "project_sponsored": self.object.sponsored,
                "project_large_company": self.object.large_company,
                "project_is_open_source": self.object.is_open_source,
                "project_is_for_sale": self.object.is_for_sale,
                "project_has_github_url": bool(self.object.github_url),
                "project_has_twitter_url": bool(self.object.twitter_url),
            },
            groups={"project": str(self.object.id)},
        )
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["newsletter_form"] = NewsletterSignupForm
        context["project_screenshot_url"] = self.request.build_absolute_uri(static("vendors/images/logo.png"))

        try:
            if self.object.homepage_screenshot:
                context["project_screenshot_url"] = self.request.build_absolute_uri(self.object.homepage_screenshot.url)
        except ValueError:
            pass

        return context


class ProjectCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    login_url = "account_login"
    model = Project
    form_class = AddProject
    template_name = "projects/submit-project.html"
    success_url = reverse_lazy("projects")
    success_message = """
        Thanks for submitting your project! I'll let you know when it is up on the site!
    """

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Registration is handled by Django Allauth via account_signup URL
        return context

    def form_valid(self, form):
        form.instance.logged_in_maker = self.request.user
        self.object = form.save()

        async_task(save_screenshot, self.object.title, hook=screenshot_saved)
        async_task(notify_of_new_project, self.object)
        async_task(fetch_page_content, self.object.id)
        capture(
            self.request,
            "project submitted",
            properties={
                "project_id": self.object.id,
                "project_title": self.object.title,
                "project_slug": self.object.slug,
                "has_github_url": bool(self.object.github_url),
                "has_twitter_url": bool(self.object.twitter_url),
                "has_technology_suggestions": bool(self.object.technology_suggestions_by_user),
            },
            groups={"project": str(self.object.id)},
        )

        return super(ProjectCreateView, self).form_valid(form)


class ProjectUpdateView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, UpdateView):
    login_url = "account_login"
    model = Project
    form_class = ProjectUpdateViewForm
    template_name = "projects/project_detail_update.html"
    success_message = "Project updated successfully!"

    def test_func(self):
        project = self.get_object()
        user_id = self.request.user.id
        return project.logged_in_maker_id == user_id or (
            project.maker_id is not None and project.maker.user_id == user_id
        )

    def get_success_url(self):
        return reverse("project", kwargs={"slug": self.object.slug})

    def form_valid(self, form):
        response = super().form_valid(form)
        capture(
            self.request,
            "project updated",
            properties={
                "project_id": self.object.id,
                "project_title": self.object.title,
                "project_slug": self.object.slug,
                "project_is_for_sale": self.object.is_for_sale,
                "has_sale_link": bool(self.object.sale_link),
                "has_github_url": bool(self.object.github_url),
                "has_twitter_url": bool(self.object.twitter_url),
                "has_description": bool(self.object.description),
            },
            groups={"project": str(self.object.id)},
        )
        return response
