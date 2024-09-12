import os
import subprocess
import tempfile

from django.core.management.utils import get_random_secret_key
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.views.decorators.http import require_http_methods, require_POST
from django.views.generic import TemplateView

from builtwithdjango.utils import get_builtwithdjango_logger
from newsletter.views import NewsletterSignupForm

logger = get_builtwithdjango_logger(__name__)


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


class FormatHTMLView(TemplateView):
    template_name = "tools/format_html.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["newsletter_form"] = NewsletterSignupForm
        return context


@csrf_exempt
@require_http_methods(["POST"])
def format_html_endpoint(request):
    html_string = request.POST.get("html_string", "")

    if not html_string:
        logger.warning("[Format HTML] No HTML String provided")
        return JsonResponse({"error": "No HTML string provided"}, status=400)

    try:
        with tempfile.NamedTemporaryFile(mode="w+", suffix=".html", delete=False) as temp_file:
            temp_file_path = temp_file.name
            temp_file.write(html_string)

        logger.info("[Format HTML] Created tmp file. Running djlint.", file_path=temp_file_path)

        command = f"djlint {temp_file_path} --reformat --profile=django"
        subprocess.run(command, shell=True)

        logger.info("[Format HTML] Finished Running djlint")
        with open(temp_file_path, "r") as file:
            logger.info("[Format HTML] Opening formatted file")
            formatted_html = file.read()

        return JsonResponse({"formatted_html": formatted_html})

    except subprocess.CalledProcessError as e:
        logger.error("[Format HTML] Subprocess Error", error=str(e))
        return JsonResponse({"error": f"djlint error: {str(e)}"}, status=500)

    except Exception as e:
        logger.error("[Format HTML] Error", error=str(e))
        return JsonResponse({"error": f"Unexpected error: {str(e)}"}, status=500)

    finally:
        if "temp_file_path" in locals():
            try:
                os.unlink(temp_file_path)
            except Exception as e:
                logger.error(f"[Format HTML] Error deleting temporary file: {str(e)}")
