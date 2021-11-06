from django.utils.text import slugify

from jobs.models import Job


def retroactively_assign_slug():
    jobs = Job.objects.all()

    for job in jobs:
        if job.slug is None:
            print(f"Updating slug for {job.title}")
            job.slug = slugify(job.title)
            job.save()
            print(f"New slug {job.slug} is saved.")
        continue


retroactively_assign_slug()

# run with `poetry run python manage.py shell < jobs/utils.py`
