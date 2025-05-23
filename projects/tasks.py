import requests
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.mail import send_mail
from django_q.tasks import async_task

from builtwithdjango.utils import get_builtwithdjango_logger

from .models import Project

logger = get_builtwithdjango_logger(__name__)


def save_screenshot(project_title):
    project = Project.objects.get(title=project_title)

    image_url = (
        f"https://api.screenshotmachine.com?key={settings.SCREENSHOT_API_KEY}&url={project.url}&dimension=1680x876"
    )
    response = requests.get(image_url)

    logger.info(f"Getting info from {image_url}.")

    if response.status_code == 200:
        file = ContentFile(response.content)
    else:
        print(f"Error: {response.status_code} - {response.text}")

    project.homepage_screenshot.save(f"{project.title}.png", file, save=True)
    project.published = True
    project.save()


def notify_of_new_project(instance):
    message = f"""
      {instance.logged_in_maker} submitted a project ({instance.title} - {instance.url}).
    """
    send_mail(
        "New Project Submission",
        message,
        "Built with Django <rasul@builtwithdjango.com>",
        ["Built with Django <rasul@builtwithdjango.com>"],
        fail_silently=False,
    )


def notify_owner_of_new_comment(instance):
    try:
        project_instance = Project.objects.get(title=instance.project.title)
        project_owner_email = project_instance.logged_in_maker.email
    except AttributeError:
        project_owner_email = "Built with Django <rasul@builtwithdjango.com>"

    message = f"""
      {instance.author} left a comment on your project ({instance.project.url} - {instance.project}).
      Comment: {instance.comment}
    """

    send_mail(
        "New Comment on your Project",
        message,
        "Built with Django <rasul@builtwithdjango.com>",
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
        "Built with Django <rasul@builtwithdjango.com>",
        ["Built with Django <rasul@builtwithdjango.com>"],
        fail_silently=False,
    )


def check_all_projects():
    projects = Project.objects.all()

    for project in projects:
        async_task(update_project_active_status, project.id, group="Check Project Active Status")


def update_project_active_status(project_id):
    project = Project.objects.get(id=project_id)

    active = project.check_project_is_active()

    if not active:
        project.active = False
        project.save(update_fields=["active"])

    return f"Project {project.title} is active: {active}"


def fetch_page_content(project_id):
    """
    Task wrapper for fetching page content.
    """
    try:
        project = Project.objects.get(id=project_id)
        success = project.fetch_page_content()
        if success:
            async_task(analyze_project, project.id)
        return success
    except Project.DoesNotExist:
        logger.error(f"Project with ID {project_id} not found")
        return False


def analyze_project(project_id):
    """
    Task wrapper for analyzing project audience.
    """
    try:
        project = Project.objects.get(id=project_id)
        return project.analyze_content()
    except Project.DoesNotExist:
        logger.error(f"Project with ID {project_id} not found")
        return False
