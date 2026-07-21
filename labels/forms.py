from django import forms

from labels.models import Label


class LabelForm(forms.ModelForm):
    class Meta:
        model = Label
        fields = ("name",)
        labels = {
            "name": "Имя",
        }
        error_messages = {
            "name": {
                "unique": (
                    "Метка с таким именем уже существует."
                ),
            },
        }
