from pydantic import BaseModel, Field


class TweetContent(BaseModel):
    """Model to structure the tweet content."""

    tweet_text: str = Field(description="A short, engaging tweet for a new Django project. Max 280 chars.")


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
