from django.contrib import admin

from .models import Comment, Post, Tag


class CommentInline(admin.TabularInline):
    model = Comment


admin.site.register(Comment)


class PostAdmin(admin.ModelAdmin):
    list_display = ("title", "created", "created", "modified")


admin.site.register(Post, PostAdmin)


admin.site.register(Tag)
