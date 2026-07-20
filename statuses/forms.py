from django import forms

from statuses.models import Status


class StatusForm(forms.ModelForm):
    class Meta:
        model = Status
        fields = ("name",)
        labels = {
            "name": "Имя",
        }
        error_messages = {
            "name": {
                "unique": (
                    "Статус с таким именем уже существует."
                ),
            },
        }
