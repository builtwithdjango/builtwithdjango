from enum import Enum

from cloudinary.models import CloudinaryField
from django.conf import settings
from django.db import models
from model_utils.models import TimeStampedModel


class Post(TimeStampedModel):
    DRAFT = "DR"
    PUBLISHED = "PB"
    PUBLISH_STATUS = [
        (DRAFT, "DRAFT"),
        (PUBLISHED, "PUBLISHED"),
    ]

    title = models.CharField(max_length=250)
    description = models.TextField(blank=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="post")
    slug = models.SlugField(max_length=250)
    tags = models.ManyToManyField("Tag", related_name="post", blank=True)
    content = models.TextField()

    status = models.CharField(
        max_length=3,
        choices=PUBLISH_STATUS,
        default=DRAFT,
    )

    unsplashID = models.CharField(max_length=40, blank=True)
    thumbnail = CloudinaryField(
        "Image", overwrite=True, resource_type="image", folder=f"blog-thumbnail-{settings.ENV}", blank=True, null=True
    )

    class Meta:
        ordering = ("-created",)

    def __str__(self):
        return self.title


class Tag(TimeStampedModel):
    name = models.CharField(max_length=50)
    slug = models.SlugField(unique=True, null=True, blank=True)

    def __str__(self):
        return self.name
