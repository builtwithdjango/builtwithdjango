from rest_framework import serializers

from blog.models import Post, Tag
from projects.models import Like


class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ("author", "project", "like", "id")
        read_only_fields = ("author", "id")


class LikeSerializerNoId(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ("author", "project", "like")
        read_only_fields = ("author", "project")


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ("id", "name", "slug")
        read_only_fields = ("slug",)


class PostSerializer(serializers.ModelSerializer):
    tags = serializers.CharField(write_only=True, required=False, allow_blank=True)
    tag_list = TagSerializer(many=True, read_only=True, source="tags")

    class Meta:
        model = Post
        fields = (
            "id",
            "author",
            "title",
            "description",
            "slug",
            "tags",
            "tag_list",
            "content",
            "status",
            "type",
            "level",
            "unsplashID",
            "created",
            "modified",
        )
        read_only_fields = ("id", "author", "created", "modified", "tag_list")

    def create(self, validated_data):
        tags_string = validated_data.pop("tags", None)

        if "author" not in validated_data:
            request = self.context.get("request")
            user = getattr(request, "user", None)
            if not getattr(user, "is_authenticated", False):
                raise serializers.ValidationError("Authenticated author is required.")
            validated_data["author"] = user

        if "level" not in validated_data:
            validated_data["level"] = Post.BEGINNER

        post = Post.objects.create(**validated_data)
        self.set_tags(post, tags_string)

        return post

    def update(self, instance, validated_data):
        tags_string = validated_data.pop("tags", None)
        post = super().update(instance, validated_data)
        self.set_tags(post, tags_string)
        return post

    def set_tags(self, post, tags_string):
        if tags_string is None:
            return

        post.tags.clear()
        tag_names = [name.strip() for name in tags_string.split(",") if name.strip()]
        for tag_name in tag_names:
            tag, _created = Tag.objects.get_or_create(
                name=tag_name,
                defaults={"slug": tag_name.lower().replace(" ", "-")},
            )
            post.tags.add(tag)
