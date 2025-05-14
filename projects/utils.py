import os

from asgiref.sync import sync_to_async
from django.conf import settings
from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext
from twikit import Client

from builtwithdjango.utils import get_builtwithdjango_logger

from .models import Project

logger = get_builtwithdjango_logger(__name__)


class TweetContent(BaseModel):
    """Model to structure the tweet content."""

    tweet_text: str = Field(
        description="A short, engaging tweet for a new Django project. Max 280 chars. Include relevant hashtags."
    )


class ProjectContext(BaseModel):
    """Model to structure the project context."""

    title: str = Field(description="The title of the project.")
    short_description: str = Field(description="A very brief description of the project.")
    url: str = Field(description="The URL of the project.")
    is_open_source: bool = Field(description="Whether the project is open source.")
    twitter_url: str = Field(description="The URL of the project's Twitter profile.")
    target_audience: str = Field(description="The target audience of the project.")
    content_summary: str = Field(description="A summary of the project's content.")
    key_features: str = Field(description="The key features of the project.")
    pain_points: str = Field(description="The pain points of the project.")


async def create_tweet(project_id):
    logger.info(f"Starting create_tweet for project_id: {project_id}")
    try:
        project = await sync_to_async(Project.objects.get)(id=project_id)
    except Project.DoesNotExist:
        raise ValueError(f"Project with id {project_id} does not exist.")

    agent = Agent(
        "google-gla:gemini-2.5-flash-preview-04-17",
        system_prompt="""
        You are an expert in crafting engaging and concise tweets for new software projects.
        The tweet should highlight the project's title and a very brief description.
        It must include a link to the project on builtwithdjango.com.
        Do not use hashtags.
        Keep the tweet within the 280-character limit.
        Output only the tweet text.
        """,
        result_type=TweetContent,
        deps_type=ProjectContext,
    )

    @agent.system_prompt
    def add_project_context(ctx: RunContext[ProjectContext]) -> str:
        return (
            "Project context:"
            f"Title: {ctx.deps.title}"
            f"Short Description: {ctx.deps.short_description}"
            f"URL: {ctx.deps.url}"
            f"Is Open Source: {ctx.deps.is_open_source}"
            f"Twitter URL: {ctx.deps.twitter_url}"
            f"Target Audience: {ctx.deps.target_audience}"
            f"Content Summary: {ctx.deps.content_summary}"
            f"Key Features: {ctx.deps.key_features}"
            f"Pain Points: {ctx.deps.pain_points}"
        )

    @agent.system_prompt
    def previous_examples() -> str:
        return """Below are some examples of tweets for other projects I did in the past:
        ---
        Codeishot (@Codeish0t) is the one place to store, manage and share your code!
        https://builtwithdjango.com/projects/codeishot
        ---
        Apivault is a completely free and open source portal that contains all the public APIs available online, so you can get inspired for new projects!
        https://builtwithdjango.com/projects/apivault
        ---
        Check out Django TV by @webology 👀
        https://builtwithdjango.com/projects/django-tv
        ---
        PDF Deck makes it super easy to share your PDFs with a simple link 🔗
        https://builtwithdjango.com/projects/pdf-deck
        ---
        Hovercode helps companies drive engagement and track results with dynamic (and pretty) QR codes
        https://builtwithdjango.com/projects/hovercode
        ---
        Check out this cool project by @anthonynsimon
        UseWebhook helps you capture and inspect webhooks from your browser. Forward to localhost, or replay requests from history.
        https://builtwithdjango.com/projects/usewebhook
        ---
        New project :)

        Cardie is an open source business card designer and sharing platform.
        https://builtwithdjango.com/projects/cardie
        ---
        Couple of cool projects were added to the directory recently. Here is the first one.

        @pingojo is a recruitment platform that connects job seekers, companies, and independent recruiters in a unique and efficient way.
        https://builtwithdjango.com/projects/pingojo
        ---
        Paul just shared his Django SaaS boileplate on built with django. It's free 👀 😍
        https://builtwithdjango.com/projects/django-saas-boilerplate
        ---
        """

    @agent.system_prompt
    def use_twitter_handle(ctx: RunContext[ProjectContext]) -> str:
        return f"Only use the Twitter handle of the project owner: {ctx.deps.twitter_url}"

    logger.info(f"Running agent for project: {project.title}")
    result = await agent.run(
        "Generate a tweet for this project",
        deps=ProjectContext(
            title=project.title,
            short_description=project.short_description,
            url=project.get_absolute_url(),
            is_open_source=project.is_open_source,
            twitter_url=project.twitter_url,
            target_audience=project.target_audience,
            content_summary=project.content_summary,
            key_features=project.key_features,
            pain_points=project.pain_points,
        ),
    )
    logger.info(f"Agent finished for project: {project.title}")

    logger.info(f"Finished create_tweet for project_id: {project_id}. Tweet: {result.data.tweet_text}")
    return result.data.tweet_text


async def tweet_project(project_id):
    logger.info(f"Starting tweet_project for project_id: {project_id}")
    try:
        project = await sync_to_async(Project.objects.get)(id=project_id)
    except Project.DoesNotExist:
        raise ValueError(f"Project with id {project_id} does not exist.")

    logger.info(f"Creating tweet content for project: {project.title}")
    tweet_text = await create_tweet(project_id)
    logger.info(f"Tweet content created for project: {project.title}. Tweet: {tweet_text}")

    client = Client("en-US")
    logger.info(f"Logging in to Twitter for project: {project.title}")
    await client.login(
        auth_info_1=settings.TWITTER_USERNAME,
        auth_info_2=settings.TWITTER_EMAIL,
        password=settings.TWITTER_PASSWORD,
    )
    logger.info(f"Logged in to Twitter for project: {project.title}")
    logger.info(f"Creating tweet on Twitter for project: {project.title}")
    await client.create_tweet(text=tweet_text)
    logger.info(f"Tweet created on Twitter for project: {project.title}")
    logger.info(f"Finished tweet_project for project_id: {project_id}")
    return tweet_text
