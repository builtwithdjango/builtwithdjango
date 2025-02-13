import requests
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.mail import send_mail
from django.utils import timezone
from django_q.tasks import async_task
from pydantic import BaseModel, Field
from pydantic_ai import Agent

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
    project.save(update_fields=["published", "homepage_screenshot"])


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
    Fetch page content using Jina Reader API and update the project model.
    """
    from projects.models import Project

    try:
        project = Project.objects.get(id=project_id)
    except Project.DoesNotExist:
        logger.error(f"Project with ID {project_id} not found")
        return False

    try:
        html_response = requests.get(project.url, timeout=30)
        html_response.raise_for_status()
        html_content = html_response.text
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching HTML content: {str(e)}")
        html_content = ""

    jina_url = f"{settings.JINA_READER_BASE_URL}/{project.url}"
    headers = {"Accept": "application/json", "Authorization": f"Bearer {settings.JINA_READER_API_KEY}"}

    try:
        response = requests.get(jina_url, headers=headers, timeout=30)
        response.raise_for_status()

        data = response.json().get("data", {})

        project.page_title = data.get("title", "")
        project.page_description = data.get("description", "")
        project.page_content_markdown = data.get("content", "")
        project.page_content_html = html_content
        project.date_scraped = timezone.now()

        project.save(
            update_fields=[
                "page_title",
                "page_description",
                "page_content_markdown",
                "page_content_html",
                "date_scraped",
            ]
        )

        logger.info(f"Successfully fetched content for project: {project.title}")
        async_task(analyze_project_audience, project.id)
        return True

    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching content from Jina Reader API: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error while fetching page content: {str(e)}")
        return False


class ProjectContent(BaseModel):
    """Model to structure the project content for analysis."""

    title: str
    description: str
    content: str
    html_content: str


class AudienceAnalysis(BaseModel):
    """Model to structure the audience analysis response."""

    target_audience: str = Field(description="The primary target audience for this project")
    audience_characteristics: list[str] = Field(description="Key characteristics of the target audience", max_items=5)
    confidence_score: int = Field(description="Confidence score for this analysis (1-100)", ge=1, le=100)


def analyze_project_audience(project_id):
    """
    Analyze the target audience of a project using PydanticAI and Google Gemini.
    """
    from projects.models import Project

    try:
        project = Project.objects.get(id=project_id)

        project_content = ProjectContent(
            title=project.page_title,
            description=project.page_description,
            content=project.page_content_markdown,
            html_content=project.page_content_html,
        )

        agent = Agent(
            "gemini-2.0-flash",
            system_prompt="""
            You are an expert in analyzing web applications and their target audiences.
            Analyze the provided content and determine the target audience of this project.
            Focus on identifying the primary user base and their key characteristics.
            Base your analysis on the actual content, features, and language used in the project.
            """,
            result_type=AudienceAnalysis,
        )

        result = agent.run_sync(
            f"""
            Please analyze this project and determine its target audience.

            Project Title: {project_content.title}
            Project Description: {project_content.description}

            Detailed Content:
            {project_content.content}

            Provide a detailed analysis of who this project is meant for.
            """
        )

        logger.info(f"Successfully analyzed audience for project: {project.title}")
        logger.info(f"Analysis results: {result.data}")

        project.audience_analysis = {
            "target_audience": result.data.target_audience,
            "characteristics": result.data.audience_characteristics,
            "confidence_score": result.data.confidence_score,
        }
        project.save(update_fields=["audience_analysis"])
        return True

    except Project.DoesNotExist:
        logger.error(f"Project with ID {project_id} not found")
        return False
    except Exception as e:
        logger.error(f"Error analyzing project audience: {str(e)}")
        return False
