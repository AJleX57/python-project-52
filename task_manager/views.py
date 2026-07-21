from django.views.generic import TemplateView
from django.views import View


class IndexView(TemplateView):
    """Отображает главную страницу менеджера задач."""

    template_name = "index.html"


class RollbarTestView(View):
    """Создаёт тестовую ошибку для проверки Rollbar."""

    def get(self, request, *args, **kwargs):
        raise RuntimeError("Test error from Task Manager")
