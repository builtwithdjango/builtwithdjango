import asyncio

from django.contrib import admin, messages

from .models import Comment, Like, Project, Technology
from .utils import tweet_project


class CommentInline(admin.TabularInline):
    model = Comment


class LikeInline(admin.TabularInline):
    model = Like


def tweet_selected_projects(modeladmin, request, queryset):
    """Admin action to tweet about selected projects."""
    tweeted = 0
    errors = 0
    for project in queryset:
        try:
            # Run the async tweet_project function
            asyncio.run(tweet_project(project.id))
            tweeted += 1
        except Exception as e:
            errors += 1
            modeladmin.message_user(request, f"Error tweeting about {project.title}: {e}", level=messages.ERROR)
    if tweeted:
        modeladmin.message_user(request, f"Successfully tweeted about {tweeted} project(s).", level=messages.SUCCESS)
    if errors and not tweeted:
        modeladmin.message_user(request, f"Failed to tweet about {errors} project(s).", level=messages.ERROR)


tweet_selected_projects.short_description = "Tweet about selected project(s) on Twitter"


def unpublish_selected_projects(modeladmin, request, queryset):
    """Admin action to unpublish selected projects."""
    updated = queryset.update(published=False)
    modeladmin.message_user(request, f"Successfully unpublished {updated} project(s).", level=messages.SUCCESS)


unpublish_selected_projects.short_description = "Unpublish selected project(s)"


class ProjectAdmin(admin.ModelAdmin):
    list_display = ["title", "logged_in_maker", "active", "published", "maker", "date_added", "might_be_spam"]
    inlines = [CommentInline, LikeInline]
    actions = [unpublish_selected_projects]


admin.site.register(Project, ProjectAdmin)
admin.site.register(Technology)
admin.site.register(Comment)
