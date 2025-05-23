"""builtwithdjango URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path
from django.views.generic import TemplateView

from .sitemaps import sitemaps

urlpatterns = (
    [
        path(f"{settings.ADMIN_URL}", admin.site.urls),
        path("", include("pages.urls")),
        path("projects/", include("projects.urls")),
        path("api/v1/", include("api.urls")),
        path("jobs/", include("jobs.urls")),
        path("makers/", include("makers.urls")),
        path("blog/", include("blog.urls")),
        path("newsletter/", include("newsletter.urls")),
        path("podcast/", include("podcast.urls")),
        path("developers/", include("developers.urls")),
        path("tools/", include("tools.urls")),
        path("users/", include("allauth.urls")),
        path("users/", include("users.urls")),
        path("uses", TemplateView.as_view(template_name="pages/uses.html"), name="uses"),
        path("stripe/", include("djstripe.urls", namespace="djstripe")),
        path(
            "sitemap.xml",
            sitemap,
            {"sitemaps": sitemaps},
            name="django.contrib.sitemaps.views.sitemap",
        ),
        path("robots.txt", include("robots.urls")),
    ]
    + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
)
