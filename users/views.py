from django.contrib import messages
from django.contrib.auth import (
    get_user_model,
    logout,
    update_session_auth_hash,
)
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView
from django.db.models.deletion import ProtectedError

from users.forms import LoginForm, UserForm


User = get_user_model()


class UserOwnerRequiredMixin(UserPassesTestMixin):
    """Разрешает изменение и удаление только своей учётной записи."""

    permission_denied_message = "У вас нет прав для изменения"

    def test_func(self):
        requested_user_id = self.kwargs.get("pk")

        return (
            self.request.user.is_authenticated
            and self.request.user.pk == requested_user_id
        )

    def handle_no_permission(self):
        messages.error(
            self.request,
            self.permission_denied_message,
        )
        return redirect("users:index")


class UserListView(ListView):
    """Отображает список всех пользователей."""

    model = User
    template_name = "users/user_list.html"
    context_object_name = "users"
    ordering = "id"


class UserCreateView(CreateView):
    """Регистрирует нового пользователя."""

    model = User
    form_class = UserForm
    template_name = "users/user_form.html"
    success_url = reverse_lazy("login")
    extra_context = {
        "page_title": "Регистрация",
        "button_text": "Зарегистрировать",
    }

    def form_valid(self, form):
        response = super().form_valid(form)

        messages.success(
            self.request,
            "Пользователь успешно зарегистрирован",
        )

        return response


class UserUpdateView(UserOwnerRequiredMixin, UpdateView):
    """Изменяет данные текущего пользователя."""

    model = User
    form_class = UserForm
    template_name = "users/user_form.html"
    success_url = reverse_lazy("users:index")
    extra_context = {
        "page_title": "Изменение пользователя",
        "button_text": "Изменить",
    }

    def form_valid(self, form):
        response = super().form_valid(form)

        # Форма изменяет пароль. Обновляем хеш текущей сессии,
        # чтобы пользователь не был автоматически разлогинен.
        update_session_auth_hash(
            self.request,
            self.object,
        )

        messages.success(
            self.request,
            "Пользователь успешно изменен",
        )

        return response


class UserDeleteView(UserOwnerRequiredMixin, DeleteView):
    """Удаляет учётную запись текущего пользователя."""

    model = User
    template_name = "users/user_confirm_delete.html"
    success_url = reverse_lazy("users:index")

    def form_valid(self, form):
        try:
            response = super().form_valid(form)
        except ProtectedError:
            messages.error(
                self.request,
                (
                    "Невозможно удалить пользователя, "
                    "потому что он используется"
                ),
            )
            return redirect("users:index")

        logout(self.request)
        messages.success(
            self.request,
            "Пользователь успешно удален",
        )

        return response


class UserLoginView(LoginView):
    """Выполняет вход пользователя."""

    template_name = "registration/login.html"
    authentication_form = LoginForm
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy("index")

    def form_valid(self, form):
        response = super().form_valid(form)

        messages.success(
            self.request,
            "Вы залогинены",
        )

        return response


class UserLogoutView(LogoutView):
    """Завершает пользовательскую сессию."""

    next_page = reverse_lazy("index")

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        messages.success(
            request,
            "Вы разлогинены",
        )

        return response
