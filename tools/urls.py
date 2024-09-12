from django.urls import path

from .views import GenerateDjangoSecret, generate_django_secret

urlpatterns = [
    path("django-secret/", GenerateDjangoSecret.as_view(), name="generate_django_secret_page"),
    path("generate-secret/", generate_django_secret, name="generate_django_secret"),
]
