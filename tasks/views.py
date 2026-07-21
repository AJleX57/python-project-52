from django.contrib import messages
from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    UserPassesTestMixin,
)
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    UpdateView,
)
from django_filters.views import FilterView

from tasks.filters import TaskFilter
from tasks.forms import TaskForm
from tasks.models import Task


class TaskListView(LoginRequiredMixin, FilterView):
    """Отображает и фильтрует список задач."""

    model = Task
    filterset_class = TaskFilter
    template_name = "tasks/task_list.html"
    context_object_name = "tasks"

    def get_queryset(self):
        return (
            Task.objects
            .select_related(
                "status",
                "author",
                "executor",
            )
            .prefetch_related("labels")
            .order_by("id")
        )


class TaskDetailView(LoginRequiredMixin, DetailView):
    model = Task
    template_name = "tasks/task_detail.html"
    context_object_name = "task"

    def get_queryset(self):
        return (
            Task.objects
            .select_related(
                "status",
                "author",
                "executor",
            )
            .prefetch_related("labels")
        )


class TaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    form_class = TaskForm
    template_name = "tasks/task_form.html"
    success_url = reverse_lazy("tasks:index")
    extra_context = {
        "page_title": "Создать задачу",
        "button_text": "Создать",
    }

    def form_valid(self, form):
        form.instance.author = self.request.user

        response = super().form_valid(form)

        messages.success(
            self.request,
            "Задача успешно создана",
        )

        return response


class TaskUpdateView(LoginRequiredMixin, UpdateView):
    model = Task
    form_class = TaskForm
    template_name = "tasks/task_form.html"
    success_url = reverse_lazy("tasks:index")
    extra_context = {
        "page_title": "Изменение задачи",
        "button_text": "Изменить",
    }

    def form_valid(self, form):
        response = super().form_valid(form)

        messages.success(
            self.request,
            "Задача успешно изменена",
        )

        return response


class TaskAuthorRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        task = self.get_object()

        return (
            task.author_id
            == self.request.user.id
        )

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()

        messages.error(
            self.request,
            "Задачу может удалить только ее автор",
        )

        return redirect("tasks:index")


class TaskDeleteView(
    LoginRequiredMixin,
    TaskAuthorRequiredMixin,
    DeleteView,
):
    model = Task
    template_name = "tasks/task_confirm_delete.html"
    context_object_name = "task"
    success_url = reverse_lazy("tasks:index")

    def form_valid(self, form):
        response = super().form_valid(form)

        messages.success(
            self.request,
            "Задача успешно удалена",
        )

        return response
