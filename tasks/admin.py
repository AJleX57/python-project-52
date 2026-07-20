from django.contrib import admin

from tasks.models import Task, TaskLabel


class TaskLabelInline(admin.TabularInline):
    model = TaskLabel
    extra = 1


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "status",
        "author",
        "executor",
        "created_at",
    )
    list_filter = (
        "status",
        "author",
        "executor",
    )
    search_fields = (
        "name",
        "description",
    )
    ordering = ("id",)
    inlines = (TaskLabelInline,)
