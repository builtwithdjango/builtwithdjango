from django.contrib import admin
from .models import Job, Company


class JobInline(admin.TabularInline):
    model = Job


class CompanyAdmin(admin.ModelAdmin):
    inlines = [
        JobInline,
    ]


admin.site.register(Company, CompanyAdmin)
admin.site.register(Job)
