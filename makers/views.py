from django.views.generic import ListView

from newsletter.views import NewsletterSignupForm
from .models import Maker


class MakerListView(ListView):
    model = Maker
    template_name = "makers/all_makers.html"
    queryset = Maker.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["newsletter_form"] = NewsletterSignupForm

        return context
