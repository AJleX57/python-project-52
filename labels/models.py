from django.db import models


class Label(models.Model):
    name = models.CharField(
        "Имя",
        max_length=100,
        unique=True,
    )
    created_at = models.DateTimeField(
        "Дата создания",
        auto_now_add=True,
    )

    class Meta:
        ordering = ["id"]
        verbose_name = "Метка"
        verbose_name_plural = "Метки"

    def __str__(self):
        return self.name
