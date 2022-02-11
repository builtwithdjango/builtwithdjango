import shutil

import requests
from django.conf import settings
from django.core.files.base import ContentFile

from .models import Project


def say_hello():
    print("Hello")


def save_screenshot(project_title):
    project = Project.objects.get(title=project_title)
    r = requests.get(
        f"https://shot.screenshotapi.net/screenshot?token={settings.SCREENSHOT_API_KEY}&url={project.url}"
    ).json()
    image = requests.get(r["screenshot"], stream=True)
    file = ContentFile(image.content)
    project.homepage_screenshot.save(f"{project.title}.png", file, save=True)
