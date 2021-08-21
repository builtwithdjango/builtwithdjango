from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics

from projects.models import Like

from .serializers import LikeSerializer, LikeSerializerNoId


class CreateLikeProjectAPIView(generics.ListCreateAPIView):
    queryset = Like.objects.all()
    serializer_class = LikeSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["author", "project"]


class UpdateLikeProjectAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Like.objects.all()
    serializer_class = LikeSerializerNoId
