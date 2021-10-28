from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, UpdateView

from newsletter.views import NewsletterSignupForm

from .forms import ClaimAccountForm
from .models import Maker


class MakerListView(ListView):
    model = Maker
    template_name = "makers/all_makers.html"
    queryset = Maker.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["newsletter_form"] = NewsletterSignupForm

        return context


class ClaimAccountView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Maker
    template_name = "makers/claim_account.html"
    form_class = ClaimAccountForm
    success_url = reverse_lazy("makers")
    success_message = "Account claimed successfully!"

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(ClaimAccountView, self).form_valid(form)
