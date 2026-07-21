import os
from pathlib import Path

import dj_database_url
from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent

# В локальной разработке переменные загружаются из .env.
# На Render используются переменные окружения сервиса.
load_dotenv(BASE_DIR / ".env")


def env_bool(name, default=False):
    """Преобразует переменную окружения в логическое значение."""

    value = os.getenv(name)

    if value is None:
        return default

    return value.lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "django-insecure-development-key-change-in-production",
)

DEBUG = env_bool(
    "DEBUG",
    default=False,
)


ROLLBAR_ACCESS_TOKEN = os.getenv(
    "ROLLBAR_ACCESS_TOKEN",
    "",
)

ROLLBAR_ENVIRONMENT = os.getenv(
    "ROLLBAR_ENVIRONMENT",
    "development" if DEBUG else "production",
)

ROLLBAR_TEST_ENABLED = env_bool(
    "ROLLBAR_TEST_ENABLED",
    default=False,
)


ROLLBAR = {
    "access_token": ROLLBAR_ACCESS_TOKEN,
    "environment": ROLLBAR_ENVIRONMENT,
    "branch": os.getenv(
        "RENDER_GIT_BRANCH",
        "main",
    ),
    "code_version": os.getenv(
        "RENDER_GIT_COMMIT",
    ),
    "root": str(BASE_DIR),
    "enabled": bool(ROLLBAR_ACCESS_TOKEN),
    "capture_ip": "anonymize",
    "capture_username": True,
    "include_request_body": False,
}


ALLOWED_HOSTS = [
    "webserver",
    "localhost",
    "127.0.0.1",
]

# Render автоматически передаёт домен приложения через эту переменную.
render_hostname = os.getenv("RENDER_EXTERNAL_HOSTNAME")

if render_hostname:
    ALLOWED_HOSTS.append(render_hostname)

# Дополнительные хосты можно передать через:
# ALLOWED_HOSTS=example.com,www.example.com
extra_hosts = os.getenv("ALLOWED_HOSTS", "")

if extra_hosts:
    ALLOWED_HOSTS.extend(
        host.strip()
        for host in extra_hosts.split(",")
        if host.strip()
    )

# Убираем возможные дубликаты, сохраняя порядок.
ALLOWED_HOSTS = list(dict.fromkeys(ALLOWED_HOSTS))


CSRF_TRUSTED_ORIGINS = []

render_external_url = os.getenv("RENDER_EXTERNAL_URL")

if render_external_url:
    CSRF_TRUSTED_ORIGINS.append(render_external_url)


INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_bootstrap5",
    "django_filters",
    "users.apps.UsersConfig",
    "statuses.apps.StatusesConfig",
    "labels.apps.LabelsConfig",
    "tasks.apps.TasksConfig",
]


MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

if ROLLBAR_ACCESS_TOKEN:
    MIDDLEWARE.append(
        "rollbar.contrib.django.middleware."
        "RollbarNotifierMiddleware"
    )


ROOT_URLCONF = "task_manager.urls"


TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            BASE_DIR / "templates",
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


WSGI_APPLICATION = "task_manager.wsgi.application"


# При наличии DATABASE_URL будет использован PostgreSQL.
# Без DATABASE_URL локально используется SQLite.
DATABASES = {
    "default": dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600,
        conn_health_checks=True,
    ),
}


AUTH_PASSWORD_VALIDATORS = []


LANGUAGE_CODE = "ru-ru"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


STATIC_URL = "/static/"

STATIC_ROOT = BASE_DIR / "staticfiles"

STORAGES = {
    "default": {
        "BACKEND": (
            "django.core.files.storage.FileSystemStorage"
        ),
    },
    "staticfiles": {
        "BACKEND": (
            "whitenoise.storage."
            "CompressedManifestStaticFilesStorage"
        ),
    },
}


DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# Render завершает HTTPS-соединение на своём прокси и передаёт
# исходный протокол в X-Forwarded-Proto.
SECURE_PROXY_SSL_HEADER = (
    "HTTP_X_FORWARDED_PROTO",
    "https",
)

# В CI и локально эти параметры по умолчанию отключены.
# На Render они включаются через переменные окружения.
SECURE_SSL_REDIRECT = env_bool(
    "SECURE_SSL_REDIRECT",
    default=False,
)

SESSION_COOKIE_SECURE = env_bool(
    "SESSION_COOKIE_SECURE",
    default=False,
)

CSRF_COOKIE_SECURE = env_bool(
    "CSRF_COOKIE_SECURE",
    default=False,
)


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "django": {
            "handlers": [
                "console",
            ],
            "level": os.getenv(
                "DJANGO_LOG_LEVEL",
                "INFO",
            ),
            "propagate": False,
        },
    },
}


LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "index"
LOGOUT_REDIRECT_URL = "index"
