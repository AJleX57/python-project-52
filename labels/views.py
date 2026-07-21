from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models.deletion import ProtectedError
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    ListView,
    UpdateView,
)

from labels.forms import LabelForm
from labels.models import Label


class LabelListView(LoginRequiredMixin, ListView):
    """Отображает список всех меток."""

    model = Label
    template_name = "labels/label_list.html"
    context_object_name = "labels"
    ordering = "id"


class LabelCreateView(LoginRequiredMixin, CreateView):
    """Создаёт новую метку."""

    model = Label
    form_class = LabelForm
    template_name = "labels/label_form.html"
    success_url = reverse_lazy("labels:index")
    extra_context = {
        "page_title": "Создать метку",
        "button_text": "Создать",
    }

    def form_valid(self, form):
        response = super().form_valid(form)

        messages.success(
            self.request,
            "Метка успешно создана",
        )

        return response


class LabelUpdateView(LoginRequiredMixin, UpdateView):
    """Изменяет существующую метку."""

    model = Label
    form_class = LabelForm
    template_name = "labels/label_form.html"
    success_url = reverse_lazy("labels:index")
    extra_context = {
        "page_title": "Изменение метки",
        "button_text": "Изменить",
    }

    def form_valid(self, form):
        response = super().form_valid(form)

        messages.success(
            self.request,
            "Метка успешно изменена",
        )

        return response


class LabelDeleteView(LoginRequiredMixin, DeleteView):
    """Удаляет метку, если она не связана с задачами."""

    model = Label
    template_name = "labels/label_confirm_delete.html"
    success_url = reverse_lazy("labels:index")

    def form_valid(self, form):
        # Понятная предварительная проверка связи с задачами.
        if self.object.tasks.exists():
            messages.error(
                self.request,
                "Невозможно удалить метку",
            )
            return redirect("labels:index")

        try:
            response = super().form_valid(form)
        except ProtectedError:
            # Дополнительная защита на уровне базы данных.
            messages.error(
                self.request,
                "Невозможно удалить метку",
            )
            return redirect("labels:index")

        messages.success(
            self.request,
            "Метка успешно удалена",
        )

        return response
