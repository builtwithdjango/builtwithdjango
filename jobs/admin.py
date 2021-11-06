from django.contrib import admin

from .models import Company, Job


class JobInline(admin.TabularInline):
    model = Job


class JobAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}


class CompanyAdmin(admin.ModelAdmin):
    inlines = [
        JobInline,
    ]


admin.site.register(Company, CompanyAdmin)
admin.site.register(Job, JobAdmin)
