from django.contrib import admin
from .models import Project, Maker, Comment, Technology


class CommentInline(admin.TabularInline):
    model = Comment


class ProjectAdmin(admin.ModelAdmin):
    inlines = [
        CommentInline,
    ]


admin.site.register(Project, ProjectAdmin)
admin.site.register(Maker)
admin.site.register(Technology)
admin.site.register(Comment)
