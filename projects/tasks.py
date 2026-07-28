import requests
from django.conf import settings
from django.core.files.base import ContentFile
from django_q.tasks import async_task

from builtwithdjango.notifications import send_admin_notification
from builtwithdjango.sentry_utils import sentry_count, sentry_task_transaction
from builtwithdjango.utils import get_builtwithdjango_logger

from .models import Project

logger = get_builtwithdjango_logger(__name__)


def save_screenshot(project_id):
    project = Project.objects.get(id=project_id)

    image_url = (
        f"https://api.screenshotmachine.com?key={settings.SCREENSHOT_API_KEY}&url={project.url}&dimension=1680x876"
    )

    logger.info(f"Getting info from {image_url}.")
    try:
        response = requests.get(image_url, timeout=30)
        response.raise_for_status()
    except requests.RequestException as e:
        logger.error("screenshot_fetch_failed", project_id=project.id, error=str(e))
        return False

    file = ContentFile(response.content)
    project.homepage_screenshot.save(f"{project.title}.png", file, save=True)
    project.published = True
    project.save()
    return True


def notify_of_new_project(instance):
    message = f"""
      {instance.logged_in_maker} submitted a project ({instance.title} - {instance.url}).
    """
    return send_admin_notification("New Project Submission", message)


def notify_owner_of_new_comment(instance):
    # Comments are temporarily disabled to mitigate abuse.
    return


def notify_admins_of_comment(instance):
    # Comments are temporarily disabled to mitigate abuse.
    return


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
    sentry_count("projects.content_fetch.started")
    with sentry_task_transaction("projects.tasks.fetch_page_content", attributes={"project.id": project_id}):
        try:
            project = Project.objects.get(id=project_id)
            success = project.fetch_page_content()
            sentry_count(
                "projects.content_fetch.completed",
                attributes={"outcome": "success" if success else "failure"},
            )
            if success:
                async_task(analyze_project, project.id)
            return success
        except Project.DoesNotExist:
            sentry_count("projects.content_fetch.completed", attributes={"outcome": "missing_project"})
            logger.error(f"Project with ID {project_id} not found")
            return False
        except Exception:
            sentry_count("projects.content_fetch.completed", attributes={"outcome": "failure"})
            raise


def analyze_project(project_id):
    """
    Task wrapper for analyzing project audience.
    """
    sentry_count("projects.content_analysis.started")
    with sentry_task_transaction("projects.tasks.analyze_project", attributes={"project.id": project_id}):
        try:
            project = Project.objects.get(id=project_id)
            success = project.analyze_content()
            project.refresh_from_db(fields=["might_be_spam"])
            sentry_count(
                "projects.content_analysis.completed",
                attributes={
                    "outcome": "success" if success else "failure",
                    "might_be_spam": project.might_be_spam,
                },
            )
            return success
        except Project.DoesNotExist:
            sentry_count("projects.content_analysis.completed", attributes={"outcome": "missing_project"})
            logger.error(f"Project with ID {project_id} not found")
            return False
        except Exception:
            sentry_count("projects.content_analysis.completed", attributes={"outcome": "failure"})
            raise
