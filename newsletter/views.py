from django.views.generic import TemplateView, CreateView
from .models import Emails
from .forms import NewsletterSignupForm
from django.urls import reverse_lazy


class NewsletterSignupView(CreateView):
    template_name = "newsletter/email-form.html"
    form_class = NewsletterSignupForm
    model = Emails
    success_url = reverse_lazy('newsletter-thanks')
    

class NewsletterThanksView(TemplateView):
    template_name = "newsletter/sucessfull-email-submit.html"
