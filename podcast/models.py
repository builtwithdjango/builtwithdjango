from django.db import models
from django.urls import reverse


class Episode(models.Model):
    created_datetime = models.DateTimeField(auto_now_add=True)
    updated_datetime = models.DateTimeField(auto_now=True)

    title = models.CharField(max_length=100)
    player_html_embed = models.TextField()
    details = models.TextField()
    show_notes = models.TextField(blank=True)
    transcript = models.TextField(blank=True)

    maker = models.ManyToManyField(
        "projects.Maker", related_name="podcast_episodes", blank=True
    )
    project = models.ManyToManyField(
        "projects.Project", related_name="podcast_episodes", blank=True
    )

    def __str__(self):
        return f"{self.title}"
