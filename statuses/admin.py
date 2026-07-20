from django.contrib import admin

from statuses.models import Status


@admin.register(Status)
class StatusAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "created_at",
    )
    search_fields = ("name",)
    ordering = ("id",)
