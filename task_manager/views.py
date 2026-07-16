from django.http import HttpRequest, HttpResponse


def index(request: HttpRequest) -> HttpResponse:
    """Отображает главную страницу приложения."""
    return HttpResponse("Привет от Хекслета!")
