from django.views.generic import TemplateView


class IndexView(TemplateView):
    """Отображает главную страницу менеджера задач."""

    template_name = "index.html"