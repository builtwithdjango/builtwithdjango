from django.views.generic import TemplateView

from projects.models import Project
from newsletter.views import NewsletterSignupForm


class HomeView(TemplateView):
    template_name = "pages/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["newsletter_form"] = NewsletterSignupForm
        context["object_list"] = Project.objects.filter(published=True)

        return context


class DonateOneTimeView(TemplateView):
    template_name = "pages/donate-one-time.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["newsletter_form"] = NewsletterSignupForm

        return context


class DonateSubscriptionView(TemplateView):
    template_name = "pages/donate-subscription.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["newsletter_form"] = NewsletterSignupForm

        return context
