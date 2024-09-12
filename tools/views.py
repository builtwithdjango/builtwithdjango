from django.core.management.utils import get_random_secret_key
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST
from django.views.generic import TemplateView

from newsletter.views import NewsletterSignupForm


class GenerateDjangoSecret(TemplateView):
    template_name = "tools/generate_django_secret.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["newsletter_form"] = NewsletterSignupForm
        return context


@csrf_protect
@require_POST
def generate_django_secret(request):
    secret_key = get_random_secret_key()
    return JsonResponse({"secret_key": secret_key})
