from django.core.management.base import BaseCommand
from django.db.models import Q
from django_q.tasks import async_task

from projects.models import Project


class Command(BaseCommand):
    help = "Schedule content fetch for projects without target audience"

    def handle(self, *args, **kwargs):
        empty_projects = Project.objects.filter(Q(page_content_markdown__isnull=True) | Q(page_content_markdown=""))

        total_projects = empty_projects.count()
        scheduled = 0

        self.stdout.write(f"Found {total_projects} projects without content analysis")

        for project in empty_projects:
            try:
                async_task("projects.tasks.fetch_page_content", project.id, task_name=f"fetch_content_{project.id}")
                scheduled += 1
                self.stdout.write(
                    self.style.SUCCESS(f"Scheduled content fetch for project: {project.title} (ID: {project.id})")
                )
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error scheduling task for project {project.id}: {str(e)}"))

        self.stdout.write(
            self.style.SUCCESS(f"Successfully scheduled tasks for {scheduled} out of {total_projects} projects")
        )
