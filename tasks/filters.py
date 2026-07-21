import django_filters
from django import forms
from django.contrib.auth import get_user_model

from labels.models import Label
from statuses.models import Status
from tasks.models import Task


User = get_user_model()


class TaskFilter(django_filters.FilterSet):
    """Фильтрует список задач по параметрам из GET-запроса."""

    status = django_filters.ModelChoiceFilter(
        field_name="status",
        queryset=Status.objects.order_by("name"),
        label="Статус",
    )

    executor = django_filters.ModelChoiceFilter(
        field_name="executor",
        queryset=User.objects.order_by("username"),
        label="Исполнитель",
    )

    labels = django_filters.ModelChoiceFilter(
        field_name="labels",
        queryset=Label.objects.order_by("name"),
        label="Метка",
        distinct=True,
    )

    self_tasks = django_filters.BooleanFilter(
        method="filter_self_tasks",
        label="Только свои задачи",
        widget=forms.CheckboxInput(),
    )

    class Meta:
        model = Task
        fields = (
            "status",
            "executor",
            "labels",
            "self_tasks",
        )

    def filter_self_tasks(
        self,
        queryset,
        name,
        value,
    ):
        """Оставляет только задачи текущего пользователя."""

        if not value:
            return queryset

        user = getattr(
            self.request,
            "user",
            None,
        )

        if user is None or not user.is_authenticated:
            return queryset.none()

        return queryset.filter(author=user)
