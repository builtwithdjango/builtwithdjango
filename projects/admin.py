from django.contrib import admin

from .models import Comment, Like, Project, Technology


class CommentInline(admin.TabularInline):
    model = Comment


class LikeInline(admin.TabularInline):
    model = Like


class ProjectAdmin(admin.ModelAdmin):
    list_display = ["title", "logged_in_maker", "active", "published", "maker", "date_added", "might_be_spam"]
    inlines = [CommentInline, LikeInline]


admin.site.register(Project, ProjectAdmin)
admin.site.register(Technology)
admin.site.register(Comment)
