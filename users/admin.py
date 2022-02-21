from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser


class CustomUserAdmin(UserAdmin):
    list_display = ["date_joined", "username", "email", "first_name", "last_name"]
    model = CustomUser

    fieldsets = UserAdmin.fieldsets + (
        (
            "Extra Fields",
            {
                "fields": (
                    "profile_image",
                    "referred_by",
                    "slug",
                    "make_public",
                    "twitter_handle",
                    "github_handle",
                    "indiehackers_handle",
                    "personal_website",
                    "interviewed",
                    "short_bio",
                )
            },
        ),
    )


admin.site.register(CustomUser, CustomUserAdmin)
