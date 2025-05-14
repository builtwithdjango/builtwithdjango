import requests
from autoslug import AutoSlugField
from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone
from model_utils.models import TimeStampedModel
from pydantic import BaseModel, Field
from pydantic_ai import Agent

from builtwithdjango.utils import get_builtwithdjango_logger

logger = get_builtwithdjango_logger(__name__)


class Project(models.Model):
    """Model for a Project."""

    date_added = models.DateTimeField(auto_now_add=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    # Required Information
    title = models.CharField(max_length=100, unique=True)
    url = models.URLField(unique=True)
    short_description = models.CharField(max_length=200)
    user_email = models.EmailField(blank=True, null=True)
    slug = AutoSlugField(populate_from="title", always_update=True)
    published = models.BooleanField(default=False)
    large_company = models.BooleanField(default=False)
    type = models.CharField(max_length=50, blank=True)
    is_profitable = models.BooleanField(default=False)
    active = models.BooleanField(default=True)

    # Optional Website Information
    is_open_source = models.BooleanField(default=False)
    description = models.TextField(blank=True)
    homepage_screenshot = models.ImageField(upload_to="website_homepage_screenshot/", blank=True)
    twitter_url = models.URLField(blank=True)
    github_url = models.URLField(blank=True)

    logged_in_maker = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="project", blank=True, null=True
    )

    technologies = models.ManyToManyField("Technology", related_name="projects", blank=True)

    ### Ideally I would automatically parse suggestions, but
    ### Will have to manually add those technologies :shrug
    technology_suggestions_by_user = models.TextField(blank=True)

    is_for_sale = models.BooleanField(default=False)
    sponsored = models.BooleanField(default=False)
    sale_link = models.URLField(blank=True)

    # To remove
    additional_info = models.TextField(blank=True)
    requirements = models.TextField(blank=True)
    maker = models.ForeignKey(
        "makers.Maker",
        related_name="projects",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    # AI Augmented Fields
    date_scraped = models.DateTimeField(blank=True, null=True)
    page_content_markdown = models.TextField(blank=True)
    page_title = models.CharField(max_length=200, blank=True)
    page_description = models.TextField(blank=True)
    page_content_html = models.TextField(blank=True)

    target_audience = models.TextField(blank=True, help_text="2-3 sentences describing the target audience")
    content_summary = models.TextField(blank=True, help_text="Summary of the page content")
    might_be_spam = models.BooleanField(default=False, help_text="AI estimation if the project might be spam")
    key_features = models.TextField(blank=True, help_text="Key features of the project")
    pain_points = models.TextField(blank=True, help_text="Pain points the project addresses")
    usage_instructions = models.TextField(blank=True, help_text="How to use the product")
    page_links = models.TextField(blank=True, help_text="Links found on the page")
    content_language = models.CharField(max_length=50, blank=True, help_text="Language the page is written in")

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("project", kwargs={"slug": self.slug})

    def check_project_is_active(self):
        try:
            response = requests.get(self.url, timeout=7)
            self.active = response.status_code == 200
        except (requests.RequestException, ConnectionError, requests.exceptions.ConnectTimeout) as e:
            logger.error(f"check_project_is_active error: {e}")
            self.active = False

        return self.active

    def fetch_page_content(self):
        """
        Fetch page content using Jina Reader API and update the project.
        Returns True if successful, False otherwise.
        """
        try:
            html_response = requests.get(self.url, timeout=30)
            html_response.raise_for_status()
            html_content = html_response.text
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching HTML content: {str(e)}")
            html_content = ""

        jina_url = f"{settings.JINA_READER_BASE_URL}/{self.url}"
        headers = {"Accept": "application/json", "Authorization": f"Bearer {settings.JINA_READER_API_KEY}"}

        try:
            response = requests.get(jina_url, headers=headers, timeout=30)
            response.raise_for_status()

            data = response.json().get("data", {})

            self.page_title = data.get("title", "")
            self.page_description = data.get("description", "")
            self.page_content_markdown = data.get("content", "")
            self.page_content_html = html_content
            self.date_scraped = timezone.now()

            self.save(
                update_fields=[
                    "page_title",
                    "page_description",
                    "page_content_markdown",
                    "page_content_html",
                    "date_scraped",
                ]
            )

            logger.info(f"Successfully fetched content for project: {self.title}")
            return True

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching content from Jina Reader: {str(e)}")
            return False

    def analyze_content(self):
        """
        Comprehensive analysis of the project's content using PydanticAI and Google Gemini.
        Returns True if successful, False otherwise.
        """

        class ProjectContent(BaseModel):
            """Model to structure the project content for analysis."""

            title: str
            description: str
            content: str
            html_content: str

        class ContentAnalysis(BaseModel):
            """Model to structure the comprehensive content analysis response. All values should be in markdown format"""

            target_audience: str = Field(description="2-3 concise sentences describing who the target audience is")
            content_summary: str = Field(
                description="Summary of what the page content is, considering it's likely a Django project showcase"
            )
            might_be_spam: bool = Field(
                description="Estimation if this might be spam content (e.g., unrelated certification posts)"
            )
            key_features: str = Field(description="Key features of the project, listed in bullet points")
            pain_points: str = Field(description="Pain points that the project addresses, listed in bullet points")
            usage_instructions: str = Field(description="Brief explanation of how to use the product")
            page_links: str = Field(
                description="Links found on the page in format: '- What the link is for - actual_link'."
            )
            content_language: str = Field(description="The primary language the page is written in")

        try:
            project_content = ProjectContent(
                title=self.page_title,
                description=self.page_description,
                content=self.page_content_markdown,
                html_content=self.page_content_html,
            )

            agent = Agent(
                "gemini-2.0-flash",
                system_prompt="""
                You are an expert in analyzing web applications and digital projects.
                Analyze the provided content comprehensively, focusing on:
                1. Understanding who it's built for
                2. Detecting if it might be spam content
                3. Identifying key features and pain points
                4. Extracting useful links and understanding the content structure

                Provide clear, concise responses for each aspect requested.
                For links, use the format: "Purpose - URL"
                Be particularly vigilant in identifying spam content like unrelated certification posts.
                """,
                result_type=ContentAnalysis,
            )

            result = agent.run_sync(
                f"""
                Please analyze this project comprehensively.

                Project Title: {project_content.title}
                Project Description: {project_content.description}

                Detailed Content:
                {project_content.content}

                HTML Content:
                {project_content.html_content}

                Provide a detailed analysis covering all requested aspects.
                """
            )

            logger.info(f"Successfully analyzed content for project: {self.title}")

            # Update all the fields
            self.target_audience = result.data.target_audience
            self.content_summary = result.data.content_summary
            self.might_be_spam = result.data.might_be_spam
            self.key_features = result.data.key_features
            self.pain_points = result.data.pain_points
            self.usage_instructions = result.data.usage_instructions
            self.page_links = result.data.page_links
            self.content_language = result.data.content_language

            self.save(
                update_fields=[
                    "target_audience",
                    "content_summary",
                    "might_be_spam",
                    "key_features",
                    "pain_points",
                    "usage_instructions",
                    "page_links",
                    "content_language",
                ]
            )

            if result.data.might_be_spam:
                self.published = False
                self.save(update_fields=["published"])

            return True

        except Exception as e:
            logger.error(f"Error analyzing project content: {str(e)}")
            return False

    class Meta:
        ordering = ["-date_added"]


class Technology(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    name = models.CharField(max_length=50)
    color = models.CharField(max_length=50)
    slug = models.SlugField(
        null=True,
        unique=True,
    )

    def __str__(self):
        return self.name


class Comment(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="comments")
    comment = models.TextField(max_length=240)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        ordering = ("-created_date",)

    def __str__(self):
        return self.comment

    def get_absolute_url(self):
        return reverse("project", args=[self.project.slug])


class Like(TimeStampedModel):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="like")
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="like")
    like = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.project}: {self.author} ({self.like})"
