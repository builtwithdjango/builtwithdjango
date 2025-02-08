from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from projects.models import Like, Project

from .serializers import LikeSerializer, LikeSerializerNoId


class CreateLikeProjectAPIView(generics.ListCreateAPIView):
    queryset = Like.objects.all()
    serializer_class = LikeSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["author", "project"]


class UpdateLikeProjectAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Like.objects.all()
    serializer_class = LikeSerializerNoId


@api_view(["GET"])
@permission_classes([AllowAny])
def search_projects(request):
    query = request.GET.get("q", "")
    if not query:
        return Response([])

    projects = Project.objects.filter(
        Q(title__icontains=query) | Q(short_description__icontains=query), published=True, active=True
    ).order_by("-sponsored", "-updated_date")[:5]

    results = [
        {
            "id": project.id,
            "title": project.title,
            "slug": project.slug,
            "short_description": project.short_description,
            "screenshot": project.homepage_screenshot.url if project.homepage_screenshot else None,
            "url": project.url,
        }
        for project in projects
    ]

    return Response(results)
