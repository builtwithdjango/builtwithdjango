from django.core.management.base import BaseCommand
from django_q.tasks import async_task

from projects.models import Project


class Command(BaseCommand):
    help = "Schedule content analysis for projects that have page content but no target audience"

    def handle(self, *args, **kwargs):
        # Find projects that have page_content_markdown but no target_audience
        projects_to_analyze = Project.objects.exclude(page_content_markdown="").filter(target_audience="")

        total_projects = projects_to_analyze.count()
        scheduled = 0

        self.stdout.write(f"Found {total_projects} projects with content but no analysis")

        for project in projects_to_analyze:
            try:
                async_task("projects.tasks.analyze_project", project.id, task_name=f"analyze_content_{project.id}")
                scheduled += 1
                self.stdout.write(
                    self.style.SUCCESS(f"Scheduled content analysis for project: {project.title} (ID: {project.id})")
                )
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error scheduling analysis for project {project.id}: {str(e)}"))

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully scheduled analysis tasks for {scheduled} out of {total_projects} projects"
            )
        )
