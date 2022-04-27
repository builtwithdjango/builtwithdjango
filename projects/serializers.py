from rest_framework import serializers

from .models import Maker, Project


class ProjectsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = "__all__"


class MakersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Maker
        fields = "__all__"
