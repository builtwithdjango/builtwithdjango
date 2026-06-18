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
        if not getattr(validated_data.get("author"), "is_superuser", False):
            raise serializers.ValidationError("Superuser author is required.")

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
        if not tags_string:
            return

        tag_names = [name.strip() for name in tags_string.split(",") if name.strip()]
        if not tag_names:
            return

        post.tags.clear()
        for tag_name in tag_names:
            slug = tag_name.lower().replace(" ", "-")
            tag, _created = Tag.objects.get_or_create(slug=slug, defaults={"name": tag_name})
            post.tags.add(tag)
