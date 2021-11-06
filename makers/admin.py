from django.contrib import admin

from .models import Maker


class MakerAdmin(admin.ModelAdmin):
    # list_display = ('title', 'body',)
    prepopulated_fields = {"slug": ("first_name", "last_name")}


admin.site.register(Maker, MakerAdmin)
