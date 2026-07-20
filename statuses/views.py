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

from statuses.forms import StatusForm
from statuses.models import Status


class StatusListView(LoginRequiredMixin, ListView):
    model = Status
    template_name = "statuses/status_list.html"
    context_object_name = "statuses"
    ordering = "id"


class StatusCreateView(LoginRequiredMixin, CreateView):
    model = Status
    form_class = StatusForm
    template_name = "statuses/status_form.html"
    success_url = reverse_lazy("statuses:index")
    extra_context = {
        "page_title": "Создать статус",
        "button_text": "Создать",
    }

    def form_valid(self, form):
        response = super().form_valid(form)

        messages.success(
            self.request,
            "Статус успешно создан",
        )

        return response


class StatusUpdateView(LoginRequiredMixin, UpdateView):
    model = Status
    form_class = StatusForm
    template_name = "statuses/status_form.html"
    success_url = reverse_lazy("statuses:index")
    extra_context = {
        "page_title": "Изменение статуса",
        "button_text": "Изменить",
    }

    def form_valid(self, form):
        response = super().form_valid(form)

        messages.success(
            self.request,
            "Статус успешно изменен",
        )

        return response


class StatusDeleteView(LoginRequiredMixin, DeleteView):
    model = Status
    template_name = "statuses/status_confirm_delete.html"
    success_url = reverse_lazy("statuses:index")

    def form_valid(self, form):
        try:
            response = super().form_valid(form)
        except ProtectedError:
            messages.error(
                self.request,
                "Невозможно удалить статус",
            )
            return redirect("statuses:index")

        messages.success(
            self.request,
            "Статус успешно удален",
        )

        return response
