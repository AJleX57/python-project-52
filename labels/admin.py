from django.contrib import admin

from labels.models import Label


@admin.register(Label)
class LabelAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "created_at",
    )
    search_fields = ("name",)
    ordering = ("id",)
