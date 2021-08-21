from rest_framework import serializers

from projects.models import Like


class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ("author", "project", "like", "id")


class LikeSerializerNoId(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ("author", "project", "like")
