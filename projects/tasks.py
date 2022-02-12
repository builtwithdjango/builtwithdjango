import requests
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.mail import send_mail

from .models import Project


def save_screenshot(project_title):
    project = Project.objects.get(title=project_title)
    r = requests.get(
        f"https://shot.screenshotapi.net/screenshot?token={settings.SCREENSHOT_API_KEY}&url={project.url}"
    ).json()
    image = requests.get(r["screenshot"], stream=True)
    file = ContentFile(image.content)
    project.homepage_screenshot.save(f"{project.title}.png", file, save=True)


def notify_of_new_project(instance):
    message = f"""
      {instance.user_email} submitted a project ({instance.title} - {instance.url}).
    """
    send_mail(
        "New Project Submission",
        message,
        "rasul@builtwithdjango.com",
        ["rasul@builtwithdjango.com"],
        fail_silently=False,
    )


def notify_owner_of_new_comment(instance):
    try:
        project_instance = Project.objects.get(title=instance.project.title)
        project_owner_email = project_instance.maker.user.email
    except AttributeError:
        project_owner_email = "rasul@builtwithdjango.com"

    message = f"""
      {instance.author} left a comment on your project ({instance.project.url} - {instance.project}).
      Comment: {instance.comment}
    """

    send_mail(
        "New Comment on your Project",
        message,
        "rasul@builtwithdjango.com",
        [project_owner_email],
        fail_silently=False,
    )


def notify_admins_of_comment(instance):
    message = f"""
      {instance.author} left a comment on project {instance.project.title} - {instance.project.url}.
      Comment: {instance.comment}
    """

    send_mail(
        f"New Comment on project {instance.project.title}",
        message,
        "rasul@builtwithdjango.com",
        ["rasul@builtwithdjango.com"],
        fail_silently=False,
    )
