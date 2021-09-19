from django.contrib import admin

from .models import CistercianDateNftRequest


class CistercianDateNfttAdmin(admin.ModelAdmin):
    list_display = [
        "email",
        "wallet_public_key",
        "date_requested",
        "sent",
        "email_confirmed",
    ]


admin.site.register(CistercianDateNftRequest, CistercianDateNfttAdmin)
