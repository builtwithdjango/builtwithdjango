import logging

import requests
from django.conf import settings
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

        new_job = Job(
            submitted_datetime=job["submitted_datetime"],
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
        new_job.save()
        count += 1

    try:
        requests.get(f"{settings.HEALTHCHECKS_HOST}/c4d85df8-bc6a-446a-9c15-aff1b0b0667d", timeout=10)
    except requests.RequestException as e:
        logger.error("Ping failed: %s" % e)

    return f"{count} jobs were created."
