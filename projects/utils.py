import os

from asgiref.sync import sync_to_async
from django.conf import settings
from pydantic_ai import Agent, RunContext
from twikit import Client

from builtwithdjango.utils import get_builtwithdjango_logger
from projects.schemas import ProjectContext, TweetContent

from .models import Project

logger = get_builtwithdjango_logger(__name__)

# Global variable to store Twitter cookies in memory
TWITTER_COOKIE_DICT = None


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
        return """Below are some examples of tweets for other projects I did in the past.
        You can use them as a template to create a tweet for the project you are given.
        ---
        New Project Alert 🚨

        Codeishot (@Codeish0t) is the one place to store, manage and share your code!

        Check it out 👇
        https://builtwithdjango.com/projects/codeishot
        ---
        Just added a new project to the directory.

        Apivault is a completely free and open source portal that contains all the public APIs available online, so you can get inspired for new projects!
        https://builtwithdjango.com/projects/apivault
        ---
        Check out Django TV by @webology 👀
        https://builtwithdjango.com/projects/django-tv
        ---
        New project just landed ✈️

        PDF Deck makes it super easy to share your PDFs with a simple link 🔗
        https://builtwithdjango.com/projects/pdf-deck
        ---
        New project was just added to the directory.

        Hovercode helps companies drive engagement and track results with dynamic (and pretty) QR codes
        https://builtwithdjango.com/projects/hovercode
        ---
        Check out this cool project by @anthonynsimon

        UseWebhook helps you capture and inspect webhooks from your browser. Forward to localhost, or replay requests from history.

        👇
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
    global TWITTER_COOKIE_DICT
    logger.info(f"Starting tweet_project for project_id: {project_id}")

    try:
        project = await sync_to_async(Project.objects.get)(id=project_id)
    except Project.DoesNotExist:
        raise ValueError(f"Project with id {project_id} does not exist.")

    logger.info(f"Creating tweet content for project: {project.title}")
    tweet_text = await create_tweet(project_id)
    logger.info(f"Tweet content created for project: {project.title}. Tweet: {tweet_text}")

    client = Client("en-US")
    logged_in_successfully = False

    if TWITTER_COOKIE_DICT:
        logger.info(f"Attempting to use stored cookies for project: {project.title}")
        try:
            client.load_cookies(TWITTER_COOKIE_DICT)
            # Verify cookie validity by fetching current user's info.
            # For tweety-ns, client.get_user_info() with no args gets current user.
            user_info = await client.get_user_info()
            if user_info and user_info.id:
                logger.info(f"Successfully validated stored cookies for user: {user_info.username}.")
                logged_in_successfully = True
            else:
                logger.info("Stored cookies appear invalid or expired (no user info obtained). Clearing.")
                TWITTER_COOKIE_DICT = None  # Invalidate stored cookies
        except Exception as e:
            logger.warning(f"Failed to validate stored cookies: {e}. Clearing stored cookies.")
            TWITTER_COOKIE_DICT = None  # Invalidate stored cookies
            # Re-initialize client to ensure a clean state before credential login
            client = Client("en-US")

    if not logged_in_successfully:
        logger.info(f"Logging in to Twitter with credentials for project: {project.title}")
        try:
            await client.login(
                auth_info_1=settings.TWITTER_USERNAME,
                auth_info_2=settings.TWITTER_EMAIL,  # For tweety-ns, this is email if auth_info_1 is username
                password=settings.TWITTER_PASSWORD,
            )
            TWITTER_COOKIE_DICT = client.get_cookies()  # Store the retrieved cookie dictionary
            logger.info(f"Logged in with credentials. New cookies obtained and stored for project: {project.title}")
            logged_in_successfully = True
        except Exception as e:
            logger.error(f"Failed to login to Twitter with credentials: {e}")
            # Depending on desired behavior, you might re-raise or handle differently
            raise RuntimeError(f"Failed to login to Twitter: {e}") from e

    if logged_in_successfully:
        logger.info(f"Creating tweet on Twitter for project: {project.title}")
        try:
            await client.create_tweet(text=tweet_text)
            logger.info(f"Tweet created on Twitter for project: {project.title}")
        except Exception as e:
            logger.error(f"Failed to create tweet: {e}")
            # If tweet fails due to auth, the cookie might be bad. Consider clearing it:
            # if "authentication" in str(e).lower() or "auth" in str(e).lower():
            #     logger.info("Tweet creation failed due to potential auth issue, clearing cookie.")
            #     TWITTER_COOKIE_DICT = None
            raise RuntimeError(f"Failed to create tweet: {e}") from e
    else:
        # This state should ideally not be reached if login failures raise exceptions
        logger.error("Fatal: Not logged in after attempts, cannot create tweet.")
        raise RuntimeError("Not logged in to Twitter, cannot create tweet.")

    logger.info(f"Finished tweet_project for project_id: {project_id}")
    return tweet_text
