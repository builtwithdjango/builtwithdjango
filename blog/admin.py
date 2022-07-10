from django.contrib import admin

from .models import Comment, Post, Tag


class CommentInline(admin.TabularInline):
    model = Comment


admin.site.register(Post)
admin.site.register(Tag)
admin.site.register(Comment)
