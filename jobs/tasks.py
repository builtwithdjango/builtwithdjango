import logging
from urllib.parse import urlparse

import cloudinary.uploader
import requests
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.mail import send_mail

from .models import Job

logger = logging.getLogger(__file__)


def notify_of_new_job(instance):
    message = f"""
      Someone submitted a new job.
      Instance: {instance}
    """
    send_mail(
        "New Job Submission",
        message,
        "Built with Django <rasul@builtwithdjango.com>",
        ["Built with Django <rasul@builtwithdjango.com>"],
        fail_silently=False,
    )


def get_latest_jobs_from_tj_alerts():
    url = settings.TJ_ALERTS_HOST + "/jobs"

    headers = {
        "Authorization": f"Bearer {settings.TJ_ALERTS_API_KEY}",
    }

    params = {"technologies": "Django"}

    response = requests.get(url, params=params, headers=headers)
    data = response.json()
    jobs = data["jobs"]

    count = 0
    for job in jobs:
        try:
            title = job["title"][0]
        except IndexError:
            title = "Software Engineer"

        if Job.objects.filter(external_id=job["id"], source="gettjalerts.com").exists():
            continue

        company_url = job["company_url"]

        new_job = Job(
            submitted_datetime=job["submitted_datetime"],
            created_datetime=job["submitted_datetime"],
            updated_datetime=job["submitted_datetime"],
            source="gettjalerts.com",
            external_id=job["id"],
            title=title,
            listing_url=f"https://gettjalerts.com/jobs/{job['id']}",
            description=job["description"],
            min_yearly_salary=job["min_salary"],
            max_yearly_salary=job["max_salary"],
            remote=job["is_remote"],
            location=job["locations"],
            company_name=job["company_name"],
        )

        if company_url:
            parsed_url = urlparse(company_url)
            domain_name = parsed_url.netloc

            try:

                image_response = cloudinary.uploader.upload(
                    f"https://logo.clearbit.com/{domain_name}",
                    public_id=f"user-profile-image-{settings.ENVIRONMENT}/{domain_name}",
                )
                new_job.company_logo = f"image/upload/v{image_response['version']}/{image_response['public_id']}"
                new_job.approved = True
            except Exception as e:
                logger.error(f"Couldn't get company_logo from Clearbit for {domain_name}")

        new_job.save()
        count += 1

    try:
        requests.get(f"{settings.HEALTHCHECKS_HOST}/c4d85df8-bc6a-446a-9c15-aff1b0b0667d", timeout=10)
    except requests.RequestException as e:
        logger.error("Ping failed: %s" % e)

    return f"{count} jobs were created."
