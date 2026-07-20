from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.db.models.deletion import ProtectedError
from django.test import TestCase
from django.urls import reverse

from statuses.models import Status


User = get_user_model()


class StatusCRUDTests(TestCase):
    fixtures = ["statuses.json"]

    def setUp(self):
        self.user = User.objects.get(
            username="status_user",
        )
        self.status = Status.objects.get(pk=1)

    def assert_flash_message(
        self,
        response,
        expected_message,
    ):
        response_messages = [
            str(message)
            for message in get_messages(
                response.wsgi_request
            )
        ]

        self.assertIn(
            expected_message,
            response_messages,
        )

    def test_pages_require_authentication(self):
        urls = [
            reverse("statuses:index"),
            reverse("statuses:create"),
            reverse(
                "statuses:update",
                kwargs={"pk": self.status.pk},
            ),
            reverse(
                "statuses:delete",
                kwargs={"pk": self.status.pk},
            ),
        ]

        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)

                self.assertRedirects(
                    response,
                    f"{reverse('login')}?next={url}",
                    fetch_redirect_response=False,
                )

    def test_post_requests_require_authentication(self):
        requests = [
            (
                reverse("statuses:create"),
                {"name": "Новый статус"},
            ),
            (
                reverse(
                    "statuses:update",
                    kwargs={"pk": self.status.pk},
                ),
                {"name": "Изменённый статус"},
            ),
            (
                reverse(
                    "statuses:delete",
                    kwargs={"pk": self.status.pk},
                ),
                {},
            ),
        ]

        for url, data in requests:
            with self.subTest(url=url):
                response = self.client.post(
                    url,
                    data,
                )

                self.assertRedirects(
                    response,
                    f"{reverse('login')}?next={url}",
                    fetch_redirect_response=False,
                )

    def test_status_list(self):
        self.client.force_login(self.user)

        response = self.client.get(
            reverse("statuses:index"),
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Новый")
        self.assertContains(response, "В работе")
        self.assertContains(
            response,
            "Создать статус",
        )

    def test_status_form_has_standard_field_name(self):
        self.client.force_login(self.user)

        response = self.client.get(
            reverse("statuses:create"),
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            'name="name"',
        )
        self.assertContains(
            response,
            'id="id_name"',
        )

    def test_create_status(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("statuses:create"),
            {
                "name": "На тестировании",
            },
        )

        self.assertRedirects(
            response,
            reverse("statuses:index"),
            fetch_redirect_response=False,
        )

        self.assertTrue(
            Status.objects.filter(
                name="На тестировании",
            ).exists()
        )

        self.assert_flash_message(
            response,
            "Статус успешно создан",
        )

    def test_duplicate_status_name(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("statuses:create"),
            {
                "name": self.status.name,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "уже существует",
        )

        self.assertEqual(
            Status.objects.filter(
                name=self.status.name,
            ).count(),
            1,
        )

    def test_update_status(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse(
                "statuses:update",
                kwargs={"pk": self.status.pk},
            ),
            {
                "name": "Завершён",
            },
        )

        self.assertRedirects(
            response,
            reverse("statuses:index"),
            fetch_redirect_response=False,
        )

        self.status.refresh_from_db()

        self.assertEqual(
            self.status.name,
            "Завершён",
        )

        self.assert_flash_message(
            response,
            "Статус успешно изменен",
        )

    def test_delete_status(self):
        self.client.force_login(self.user)

        status_id = self.status.pk

        response = self.client.post(
            reverse(
                "statuses:delete",
                kwargs={"pk": status_id},
            ),
        )

        self.assertRedirects(
            response,
            reverse("statuses:index"),
            fetch_redirect_response=False,
        )

        self.assertFalse(
            Status.objects.filter(
                pk=status_id,
            ).exists()
        )

        self.assert_flash_message(
            response,
            "Статус успешно удален",
        )

    def test_protected_status_cannot_be_deleted(self):
        self.client.force_login(self.user)

        protected_error = ProtectedError(
            "Статус используется задачей",
            [self.status],
        )

        with patch.object(
            Status,
            "delete",
            side_effect=protected_error,
        ):
            response = self.client.post(
                reverse(
                    "statuses:delete",
                    kwargs={"pk": self.status.pk},
                ),
            )

        self.assertRedirects(
            response,
            reverse("statuses:index"),
            fetch_redirect_response=False,
        )

        self.assertTrue(
            Status.objects.filter(
                pk=self.status.pk,
            ).exists()
        )

        self.assert_flash_message(
            response,
            "Невозможно удалить статус",
        )
