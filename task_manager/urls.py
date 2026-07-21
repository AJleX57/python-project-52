from django.contrib import admin
from django.urls import include, path
from django.conf import settings

from task_manager.views import (
    IndexView,
    RollbarTestView,
)
from users.views import UserLoginView, UserLogoutView


urlpatterns = [
    path(
        "",
        IndexView.as_view(),
        name="index",
    ),
    path(
        "users/",
        include("users.urls"),
    ),
    path(
    "statuses/",
    include("statuses.urls"),
    ),
    path(
    "labels/",
    include("labels.urls"),
    ),
    path(
    "tasks/",
    include("tasks.urls"),
    ),
    path(
        "login/",
        UserLoginView.as_view(),
        name="login",
    ),
    path(
        "logout/",
        UserLogoutView.as_view(),
        name="logout",
    ),
    path(
        "admin/",
        admin.site.urls,
    ),
]


if settings.ROLLBAR_TEST_ENABLED:
    urlpatterns.append(
        path(
            "__rollbar_test__/",
            RollbarTestView.as_view(),
            name="rollbar-test",
        )
    )
