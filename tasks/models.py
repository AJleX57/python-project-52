from django.conf import settings
from django.db import models


class Task(models.Model):
    name = models.CharField(
        "Имя",
        max_length=200,
        unique=True,
    )
    description = models.TextField(
        "Описание",
    )
    status = models.ForeignKey(
        "statuses.Status",
        on_delete=models.PROTECT,
        related_name="tasks",
        verbose_name="Статус",
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_tasks",
        verbose_name="Автор",
    )
    executor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="assigned_tasks",
        verbose_name="Исполнитель",
        null=True,
        blank=True,
    )
    labels = models.ManyToManyField(
        "labels.Label",
        through="TaskLabel",
        through_fields=("task", "label"),
        related_name="tasks",
        verbose_name="Метки",
        blank=True,
    )
    created_at = models.DateTimeField(
        "Дата создания",
        auto_now_add=True,
    )

    class Meta:
        ordering = ["id"]
        verbose_name = "Задача"
        verbose_name_plural = "Задачи"

    def __str__(self):
        return self.name


class TaskLabel(models.Model):
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name="task_labels",
    )
    label = models.ForeignKey(
        "labels.Label",
        on_delete=models.PROTECT,
        related_name="task_labels",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("task", "label"),
                name="unique_task_label",
            ),
        ]

    def __str__(self):
        return f"{self.task} — {self.label}"
