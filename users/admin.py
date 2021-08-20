from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


class CustomUserAdmin(UserAdmin):
    model = CustomUser

    fieldsets = UserAdmin.fieldsets + (
        ("Extra Fields", {"fields": ("profile_image",)}),
    )


admin.site.register(CustomUser, CustomUserAdmin)
