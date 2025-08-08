from datetime import datetime, timedelta
from typing import Any, Dict, List

import requests
from django.conf import settings
from django.utils import timezone
from google import genai

from builtwithdjango.utils import get_builtwithdjango_logger
from jobs.models import Job
from projects.models import Project

logger = get_builtwithdjango_logger(__name__)


def get_intro_block():
    return """Hey, Happy Wednesday!

> ***Why are you getting this***: \*You signed up to receive this newsletter on [Built with Django](https://builtwithdjango.com). I promised to send you the latest projects and jobs on the site as well as any other interesting Django content I encountered during the month. *If you don't want to receive this newsletter, feel free to* [*unsubscribe*](\{\{ unsubscribe_url }}) *anytime.*
    """


def get_news_and_updates_block():
    # probably should be done manually
    # but def get the latest stuff from the changelog and use that too

    return ""


def get_projects_block():
    block = ""
    last_7_days = timezone.now() - timedelta(days=7)
    projects = Project.objects.filter(created_date__gte=last_7_days).filter(published=True)
    for project in projects:
        if project.maker:
            maker = f"by [{project.maker.first_name} {project.maker.last_name}](https://builtwithdjango.com{project.maker.get_absolute_url}):"
        else:
            maker = ""

        block += f"- [{project.title}](https://builtwithdjango.com{project.get_absolute_url}) by {maker} - {project.short_description}\n"

    return block


def get_jobs_block():
    block = ""
    last_7_days = timezone.now() - timedelta(days=7)
    jobs = Job.objects.filter(created_datetime__gte=last_7_days).filter(approved=True)
    for job in jobs:
        stars = "⭐⭐⭐" if getattr(job, "paid", False) else ""
        block += (
            f"- {stars} [{job.title} at {job.company_name}](https://builtwithdjango.com{job.get_absolute_url}){stars}\n"
        )

    return block


def get_blog_posts_block():
    # This I will get from my reader api account

    return ""


def get_top_links_block():
    # This i hopefully can pull from Buttondown

    return ""


def get_support_block():
    return """You can support this project by using one of the affiliate links below. These are always going to be projects I use and love! No "Bluehost" crap here!

- [Buttondown](https://buttondown.email/refer/rasulkireev) - Email newsletter tool I use to send you this newsletter.

- [Readwise](https://readwise.io/i/rasul) - Best reading software company out there. I you want to up your e-reading game, this is definitely for you! It also so happens that I work for Readwise. Best company out there!

- [Hetzner](https://hetzner.cloud/?ref=Ju1ttKSG0Fn7) - IMHO the best place to buy a VPS or a server for your projects. I'll be doing a tutorial on how to use this in the future.

- [SaaS Pegasus](https://www.saaspegasus.com/?via=rasul) is one of the best (if not the best) ways to quickstart your Django Project. If you have a business idea but don't want to set up all the boring stuff (Auth, Payments, Workers, etc.) this is for you!
"""


def get_latest_django_documents(limit: int = 10, days_back: int = 7) -> List[Dict[str, Any]]:
    token = settings.READWISE_API_TOKEN
    django_tag = "django"

    def fetch_documents_with_tag(tag: str, updated_after: str) -> List[Dict[str, Any]]:
        all_documents = []
        next_page_cursor = None

        while True:
            params = {"tag": tag, "updatedAfter": updated_after}
            if next_page_cursor:
                params["pageCursor"] = next_page_cursor

            try:
                response = requests.get(
                    url="https://readwise.io/api/v3/list/",
                    params=params,
                    headers={"Authorization": f"Token {token}"},
                    timeout=30,
                )
                response.raise_for_status()

                data = response.json()
                all_documents.extend(data.get("results", []))

                next_page_cursor = data.get("nextPageCursor")
                if not next_page_cursor:
                    break

            except requests.exceptions.RequestException as e:
                print(f"Error fetching documents: {e}")
                break

        return all_documents

    cutoff_date = datetime.now() - timedelta(days=days_back)
    updated_after = cutoff_date.isoformat()
    documents_with_django_tag = fetch_documents_with_tag(django_tag, updated_after)
    excluded_title_phrases = ["My Blog Posts"]
    excluded_authors = {"Python Weekly", "Tech / Daily", "Django News"}

    filtered_documents = []
    for doc in documents_with_django_tag:
        title = doc.get("title", "")
        if any(phrase in title for phrase in excluded_title_phrases):
            continue

        author = doc.get("author", "")
        if author in excluded_authors:
            continue

        filtered_documents.append(doc)

    filtered_documents.sort(key=lambda x: x.get("updated_at", ""), reverse=True)

    return filtered_documents[:limit]


def get_top_links_block(limit: int = 10, days_back: int = 7):
    docs = get_latest_django_documents(limit=limit, days_back=days_back)

    block = ""
    for doc in docs:
        block += f"- [{doc['title']}]({doc['url']}) by {doc['author']} - {doc['summary']}\n"

    return block


def prepare_newsletter():
    newsletter = ""
    newsletter += "\n\n"

    newsletter += get_intro_block()

    newsletter += "\n\n## News and Updates\n"
    newsletter += get_news_and_updates_block()

    newsletter += "\n\n## Projects\n"
    newsletter += get_projects_block()

    newsletter += "\n\n## Jobs\n"
    newsletter += get_jobs_block()

    newsletter += "\n\n## Blog Posts from the Community\n"
    newsletter += get_blog_posts_block()

    newsletter += "\n\n## Top Links from Last Issue\n"
    newsletter += get_top_links_block()

    # newsletter += "\n\n## Django Changes\n"
    # newsletter += get_django_changes_block()

    newsletter += "\n\n## Support\n"
    newsletter += get_support_block()

    return newsletter


def generate_buttondown_newsletter_subject(body: str):
    gemini_client = genai.Client(api_key=settings.GEMINI_API_KEY)

    """
    Generates a newsletter subject line using the Gemini API based on the email body.
    """
    prompt = f"""
    You are an expert copywriter specializing in email subject lines.
    Your task is to generate a killer subject line for a newsletter.

    The subject line must do two things:
    1. Hint at a benefit. For example, "How to get your first 10 sales (without a big list)" – clear benefit and it removes a mental obstacle.
    2. Create curiosity. For example, "THIS almost killed my launch" – What's "this"? What happened? Instant curiosity.

    Consider these 7 email subject line styles that consistently deliver higher open rates:
    1. Curiosity: "THIS changed everything for my business."
    2. Pain: "Still can't convert traffic into buyers?"
    3. Benefit: "How to 2X your leads in 30 days"
    4. Story: "I accidentally ordered d*ck cheese" (yes, deliverability took a hit. but replies went crazy.)
    5. Question: "Do you make these content mistakes?"
    6. Contrarian: "Why storytelling WON'T grow your brand (and what will)"
    7. Proof: "How I grew to 70,000 followers in one year"

    Use these to match your email type:
    - Sending a story? Use a story subject.
    - Giving advice? Use benefit or question.
    - Writing to sell? Use pain or proof.

    Mix them up. Shuffle them often. They never go stale.

    Here's what NOT to do:
    - Don't write "Newsletter #3" (instant death)
    - Don't ask boring yes/no questions that can be answered with a simple yes/no.
    - Don't try to be too clever (you are not Hemingway or ChatGPT).
    - Don't use bold or italic text.
    - Don't use markdown, just plain text.
    - Don't use links.
    - Don't use images.
    - Don't use videos.
    - Don't use hashtags.
    - Do use emojis where appropriate, but don't overdo it.

    The newsletter body is as follows:
    ---
    {body}
    ---

    Generate a single, compelling subject line based on the content and guidelines above.
    Only return the subject line, nothing else.
    """  # noqa: E501

    response = gemini_client.models.generate_content(
        model="gemini-2.5-pro-preview-05-06",  # Using model from user's example
        contents=prompt,
    )
    subject = getattr(response, "text", None)

    return subject.strip()


def send_buttondown_newsletter():
    now = timezone.now()
    nine_am_today = now.replace(hour=9, minute=0, second=0, microsecond=0)
    publish_date = nine_am_today.isoformat()

    body = prepare_newsletter()
    subject = generate_buttondown_newsletter_subject(body)

    url = "https://api.buttondown.com/v1/emails"
    headers = {"Authorization": f"Token {settings.BUTTONDOWN_API_KEY}"}
    data = {"subject": subject, "body": body, "publish_date": publish_date}

    response = requests.post(url, headers=headers, json=data)

    return "Success"
