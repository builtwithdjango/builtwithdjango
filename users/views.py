from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView
from django_q.tasks import async_task

from newsletter.views import NewsletterSignupForm

from .forms import CustomLoginForm, CustomUserCreationForm, CustomUserUpdateForm
from .models import CustomUser
from .tasks import notify_of_new_user


class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy("login")
    template_name = "account/signup.html"

    def get_context_data(self, **kwargs):
        context = super(SignUpView, self).get_context_data(**kwargs)
        context["newsletter_form"] = NewsletterSignupForm

        return context

    def form_valid(self, form):
        self.object = form.save()
        async_task(notify_of_new_user, self.object)

        return super(SignUpView, self).form_valid(form)


class CustomLoginView(LoginView):
    form_class = CustomLoginForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["newsletter_form"] = NewsletterSignupForm

        return context


class ProfileUpdateForm(LoginRequiredMixin, UpdateView):
    form_class = CustomUserUpdateForm
    model = CustomUser
    slug_field = "username"
    slug_url_kwarg = "username"
    success_url = reverse_lazy("home")
    template_name = "account/profile-update.html"

    def get_object(self, queryset=None):
        return self.request.user

    def get_initial(self):
        initial_base = super(ProfileUpdateForm, self).get_initial()
        initial_base["referred_by_username"] = self.request.user.referred_by

        return initial_base

    def form_valid(self, form):
        referred_by_username = form.cleaned_data.get("referred_by_username")
        try:
            referred_user = CustomUser.objects.get(username=referred_by_username)
            form.instance.referred_by = referred_user
        except CustomUser.DoesNotExist:
            self.success_url = reverse_lazy("update-profile")
            messages.warning(self.request, "Such user does not exist.")

            form.instance.referred_by = None

        return super(ProfileUpdateForm, self).form_valid(form)
