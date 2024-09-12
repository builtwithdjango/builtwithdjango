from django.urls import path

from .views import FormatHTMLView, GenerateDjangoSecret, format_html_endpoint, generate_django_secret

urlpatterns = [
    path("django-secret/", GenerateDjangoSecret.as_view(), name="generate_django_secret_page"),
    path("generate-secret/", generate_django_secret, name="generate_django_secret"),
    path("api/format-html/", format_html_endpoint, name="format_html_endpoint"),
    path("format-html/", FormatHTMLView.as_view(), name="format_html_view"),
]
