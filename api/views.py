from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, BasePermission, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from blog.models import Post
from builtwithdjango.analytics import capture
from projects.models import Like, Project

from .serializers import LikeSerializer, LikeSerializerNoId, PostSerializer


class IsSuperuser(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_superuser)


class CreateLikeProjectAPIView(generics.ListCreateAPIView):
    queryset = Like.objects.all()
    serializer_class = LikeSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["author", "project"]

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]

        return [IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        like, created = Like.objects.update_or_create(
            author=request.user,
            project=serializer.validated_data["project"],
            defaults={"like": serializer.validated_data.get("like", False)},
        )
        self.capture_like_change(like)
        response_serializer = self.get_serializer(like)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

    def capture_like_change(self, like):
        capture(
            self.request,
            "project liked" if like.like else "project unliked",
            properties={
                "project_id": like.project_id,
                "author_id": like.author_id,
                "like_id": like.id,
                "like_value": like.like,
            },
            groups={"project": str(like.project_id)},
        )


class UpdateLikeProjectAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Like.objects.all()
    serializer_class = LikeSerializerNoId

    def get_permissions(self):
        if self.request.method in {"GET", "HEAD", "OPTIONS"}:
            return [AllowAny()]

        return [IsAuthenticated()]

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.method in {"GET", "HEAD", "OPTIONS"}:
            return queryset

        return queryset.filter(author=self.request.user)

    def perform_update(self, serializer):
        like = serializer.save(author=self.request.user)
        capture(
            self.request,
            "project liked" if like.like else "project unliked",
            properties={
                "project_id": like.project_id,
                "author_id": like.author_id,
                "like_id": like.id,
                "like_value": like.like,
            },
            groups={"project": str(like.project_id)},
        )

    def perform_destroy(self, instance):
        project_id = instance.project_id
        author_id = instance.author_id
        like_id = instance.id
        instance.delete()
        capture(
            self.request,
            "project like removed",
            properties={
                "project_id": project_id,
                "author_id": author_id,
                "like_id": like_id,
            },
            groups={"project": str(project_id)},
        )


class ProjectLikeToggleAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get_requested_like(self, request):
        if "like" not in request.data:
            return None

        value = request.data["like"]
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            normalized_value = value.lower()
            if normalized_value in {"true", "1", "yes", "on"}:
                return True
            if normalized_value in {"false", "0", "no", "off"}:
                return False

        return bool(value)

    def post(self, request, project_id):
        project = generics.get_object_or_404(Project, pk=project_id)
        requested_like = self.get_requested_like(request)
        like_value = requested_like
        if like_value is None:
            existing_like = Like.objects.filter(author=request.user, project=project).first()
            like_value = not bool(existing_like and existing_like.like)

        like, _ = Like.objects.update_or_create(
            author=request.user,
            project=project,
            defaults={"like": like_value},
        )
        like_count = Like.objects.filter(project=project, like=True).count()

        capture(
            request,
            "project liked" if like.like else "project unliked",
            properties={
                "project_id": like.project_id,
                "author_id": like.author_id,
                "like_id": like.id,
                "like_value": like.like,
                "like_count": like_count,
            },
            groups={"project": str(like.project_id)},
        )

        return Response(
            {
                "project": project.id,
                "like": like.like,
                "like_count": like_count,
            },
            status=status.HTTP_200_OK,
        )


@api_view(["GET"])
@permission_classes([AllowAny])
def search_projects(request):
    query = request.GET.get("q", "")
    if not query:
        return Response([])

    projects = Project.objects.filter(
        Q(title__icontains=query) | Q(short_description__icontains=query), published=True, active=True
    ).order_by("-sponsored", "-updated_date")[:5]
    result_count = len(projects)
    capture(
        request,
        "project search performed",
        properties={
            "query": query[:120],
            "query_length": len(query),
            "result_count": result_count,
            "has_results": result_count > 0,
            "result_project_ids": [project.id for project in projects],
        },
    )

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


class BlogPostListCreateAPIView(generics.ListCreateAPIView):
    """
    List and create blog posts for token-authenticated superusers.
    """

    queryset = Post.objects.select_related("author").prefetch_related("tags")
    serializer_class = PostSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsSuperuser]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["status", "type", "level"]

    def perform_create(self, serializer):
        post = serializer.save(author=self.request.user)
        capture(
            self.request,
            "post created",
            properties={
                "post_id": post.id,
                "post_title": post.title,
                "post_slug": post.slug,
                "post_status": post.status,
                "post_type": post.type,
            },
        )


class BlogPostRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, and delete blog posts for token-authenticated superusers.
    """

    queryset = Post.objects.select_related("author").prefetch_related("tags")
    serializer_class = PostSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsSuperuser]

    def perform_update(self, serializer):
        post = serializer.save()
        capture(
            self.request,
            "post updated",
            properties={
                "post_id": post.id,
                "post_title": post.title,
                "post_slug": post.slug,
                "post_status": post.status,
                "post_type": post.type,
            },
        )

    def perform_destroy(self, instance):
        post_id = instance.id
        post_title = instance.title
        post_slug = instance.slug
        post_status = instance.status
        post_type = instance.type
        instance.delete()
        capture(
            self.request,
            "post deleted",
            properties={
                "post_id": post_id,
                "post_title": post_title,
                "post_slug": post_slug,
                "post_status": post_status,
                "post_type": post_type,
            },
        )
