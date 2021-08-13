from django.views.generic import ListView, DetailView

from .models import Episode
from newsletter.views import NewsletterSignupForm


class EpisodeListView(ListView):
    model = Episode
    template_name = "podcast/all_episodes.html"
    queryset = Episode.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["newsletter_form"] = NewsletterSignupForm

        return context


class EpisodeDetailView(DetailView):
    model = Episode
    template_name = "podcast/episode_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["newsletter_form"] = NewsletterSignupForm

        return context
