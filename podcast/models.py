from django.db import models
from django.urls import reverse


class Episode(models.Model):
    created_datetime = models.DateTimeField(auto_now_add=True)
    updated_datetime = models.DateTimeField(auto_now=True)

    title = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    thumbnail = models.ImageField(upload_to="podcast_episode_thumbnail/")
    player_html_embed = models.TextField(blank=True)
    youtube_html_embed = models.TextField(blank=True)
    details = models.TextField(blank=True)
    show_notes = models.TextField(blank=True)
    transcript = models.TextField(blank=True)

    maker = models.ManyToManyField(
        "makers.Maker", related_name="podcast_episodes", blank=True
    )
    project = models.ManyToManyField(
        "projects.Project", related_name="podcast_episodes", blank=True
    )

    class Meta:
        ordering = ["-created_datetime"]

    def __str__(self):
        return f"{self.title}"

    def get_absolute_url(self):
        return reverse("episode_details", args=[self.slug])
