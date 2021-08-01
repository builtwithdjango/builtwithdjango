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
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.sitemaps.views import sitemap
from django.contrib.sitemaps import GenericSitemap

from projects.models import Project
from .sitemaps import StaticViewSitemap

sitemaps = {
    "static": StaticViewSitemap,
    "projects": GenericSitemap(
        {
            "queryset": Project.objects.filter(published=True),
            "date_field": "date_added",
        },
        priority=0.8,
    ),
}

urlpatterns = (
    [
        path("admin/", admin.site.urls),
        path(
            "sitemap.xml",
            sitemap,
            {"sitemaps": sitemaps},
            name="django.contrib.sitemaps.views.sitemap",
        ),
        path("", include("projects.urls")),
        path("jobs/", include("jobs.urls")),
        path("newsletter/", include("newsletter.urls")),
        path("users/", include("users.urls")),
        path("users/", include("django.contrib.auth.urls")),
    ]
    + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
)
