from django import forms
from django.contrib.auth import get_user_model

from labels.models import Label
from statuses.models import Status
from tasks.models import Task


User = get_user_model()


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = (
            "name",
            "description",
            "status",
            "executor",
            "labels",
        )
        labels = {
            "name": "Имя",
            "description": "Описание",
            "status": "Статус",
            "executor": "Исполнитель",
            "labels": "Метки",
        }
        error_messages = {
            "name": {
                "unique": (
                    "Задача с таким именем уже существует."
                ),
            },
        }
        widgets = {
            "description": forms.Textarea(
                attrs={"rows": 5},
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["status"].queryset = (
            Status.objects.order_by("name")
        )
        self.fields["executor"].queryset = (
            User.objects.order_by("username")
        )
        self.fields["labels"].queryset = (
            Label.objects.order_by("name")
        )
