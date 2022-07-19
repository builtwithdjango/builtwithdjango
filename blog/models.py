from cloudinary.models import CloudinaryField
from django.conf import settings
from django.db import models
from django.urls import reverse
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

    icon = CloudinaryField(
        "Image",
        overwrite=True,
        resource_type="image",
        folder=f"blog-post-icon-{settings.ENVIRONMENT}",
        blank=True,
        null=True,
    )

    BEGINNER = "BEGINNER"
    INTERMEDIATE = "INTERMEDIATE"
    ADVANCED = "ADVANCED"
    DIFFICULTY_LEVEL = [
        (BEGINNER, "BEGINNER"),
        (INTERMEDIATE, "INTERMEDIATE"),
        (ADVANCED, "ADVANCED"),
    ]

    level = models.CharField(
        max_length=15,
        choices=DIFFICULTY_LEVEL,
        default=BEGINNER,
    )

    class Meta:
        ordering = ("-created",)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("post", kwargs={"slug": self.slug})


class Tag(TimeStampedModel):
    name = models.CharField(max_length=50)
    slug = models.SlugField(unique=True, null=True, blank=True)

    def __str__(self):
        return self.name


class Comment(TimeStampedModel):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="guide_comments")
    comment = models.TextField()
    approved = models.BooleanField(default=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="guide_comments")

    def __str__(self):
        return self.comment

    def get_absolute_url(self):
        return reverse("post", args=[self.project.slug])
