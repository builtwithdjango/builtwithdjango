from django.urls import reverse_lazy 
from django.views.generic import CreateView
from django.contrib.auth.views import LoginView

from newsletter.views import NewsletterSignupForm

from .forms import CustomUserCreationForm

class SignUpView(CreateView):
  form_class = CustomUserCreationForm
  success_url = reverse_lazy('login')
  template_name = 'registration/signup.html'

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context["form"] = NewsletterSignupForm

    return context


class LoginView(LoginView):

    def get_context_data(self, **kwargs):
      context = super().get_context_data(**kwargs)
      context["form"] = NewsletterSignupForm

      return context

