from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import reverse

from labels.models import Label
from statuses.models import Status
from tasks.models import Task


User = get_user_model()


class TaskCRUDTests(TestCase):
    fixtures = ["tasks.json"]

    def setUp(self):
        self.author = User.objects.get(
            username="task_author",
        )
        self.executor = User.objects.get(
            username="task_executor",
        )
        self.status = Status.objects.get(pk=301)
        self.second_status = Status.objects.get(pk=302)
        self.label = Label.objects.get(pk=301)
        self.task = Task.objects.get(pk=301)

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
            reverse("tasks:index"),
            reverse("tasks:create"),
            reverse(
                "tasks:detail",
                kwargs={"pk": self.task.pk},
            ),
            reverse(
                "tasks:update",
                kwargs={"pk": self.task.pk},
            ),
            reverse(
                "tasks:delete",
                kwargs={"pk": self.task.pk},
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

    def test_task_list(self):
        self.client.force_login(self.author)

        response = self.client.get(
            reverse("tasks:index"),
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            self.task.name,
        )
        self.assertContains(
            response,
            "Создать задачу",
        )
        self.assertContains(
            response,
            "Показать",
        )

    def test_task_detail(self):
        self.client.force_login(self.author)

        response = self.client.get(
            reverse(
                "tasks:detail",
                kwargs={"pk": self.task.pk},
            ),
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            self.task.name,
        )
        self.assertContains(
            response,
            self.task.description,
        )
        self.assertContains(
            response,
            self.label.name,
        )

    def test_task_form_has_standard_field_names(self):
        self.client.force_login(self.author)

        response = self.client.get(
            reverse("tasks:create"),
        )

        self.assertEqual(response.status_code, 200)

        expected_fields = (
            "name",
            "description",
            "status",
            "executor",
            "labels",
        )

        for field_name in expected_fields:
            with self.subTest(field=field_name):
                self.assertContains(
                    response,
                    f'name="{field_name}"',
                )
                self.assertContains(
                    response,
                    f'id="id_{field_name}"',
                )

    def test_create_task(self):
        self.client.force_login(self.author)

        response = self.client.post(
            reverse("tasks:create"),
            {
                "name": "Новая задача",
                "description": "Новое описание",
                "status": self.status.pk,
                "executor": self.executor.pk,
                "labels": [self.label.pk],
            },
        )

        self.assertRedirects(
            response,
            reverse("tasks:index"),
            fetch_redirect_response=False,
        )

        created_task = Task.objects.get(
            name="Новая задача",
        )

        self.assertEqual(
            created_task.author,
            self.author,
        )
        self.assertEqual(
            created_task.executor,
            self.executor,
        )
        self.assertEqual(
            created_task.status,
            self.status,
        )
        self.assertIn(
            self.label,
            created_task.labels.all(),
        )

        self.assert_flash_message(
            response,
            "Задача успешно создана",
        )

    def test_duplicate_task_name(self):
        self.client.force_login(self.author)

        response = self.client.post(
            reverse("tasks:create"),
            {
                "name": self.task.name,
                "description": "Другое описание",
                "status": self.status.pk,
                "executor": self.executor.pk,
                "labels": [],
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "уже существует",
        )

        self.assertEqual(
            Task.objects.filter(
                name=self.task.name,
            ).count(),
            1,
        )

    def test_logged_user_can_update_task(self):
        self.client.force_login(self.executor)

        response = self.client.post(
            reverse(
                "tasks:update",
                kwargs={"pk": self.task.pk},
            ),
            {
                "name": "Изменённая задача",
                "description": "Изменённое описание",
                "status": self.second_status.pk,
                "executor": self.author.pk,
                "labels": [self.label.pk],
            },
        )

        self.assertRedirects(
            response,
            reverse("tasks:index"),
            fetch_redirect_response=False,
        )

        self.task.refresh_from_db()

        self.assertEqual(
            self.task.name,
            "Изменённая задача",
        )
        self.assertEqual(
            self.task.status,
            self.second_status,
        )

        # Автор не должен изменяться через форму.
        self.assertEqual(
            self.task.author,
            self.author,
        )

        self.assert_flash_message(
            response,
            "Задача успешно изменена",
        )

    def test_author_can_delete_task(self):
        self.client.force_login(self.author)

        task_id = self.task.pk

        response = self.client.post(
            reverse(
                "tasks:delete",
                kwargs={"pk": task_id},
            ),
        )

        self.assertRedirects(
            response,
            reverse("tasks:index"),
            fetch_redirect_response=False,
        )

        self.assertFalse(
            Task.objects.filter(
                pk=task_id,
            ).exists()
        )

        self.assert_flash_message(
            response,
            "Задача успешно удалена",
        )

    def test_non_author_cannot_delete_task(self):
        self.client.force_login(self.executor)

        response = self.client.post(
            reverse(
                "tasks:delete",
                kwargs={"pk": self.task.pk},
            ),
        )

        self.assertRedirects(
            response,
            reverse("tasks:index"),
            fetch_redirect_response=False,
        )

        self.assertTrue(
            Task.objects.filter(
                pk=self.task.pk,
            ).exists()
        )

        self.assert_flash_message(
            response,
            "Задачу может удалить только ее автор",
        )

    def test_linked_status_cannot_be_deleted(self):
        self.client.force_login(self.author)

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

    def test_linked_user_cannot_be_deleted(self):
        self.client.force_login(self.author)

        response = self.client.post(
            reverse(
                "users:delete",
                kwargs={"pk": self.author.pk},
            ),
        )

        self.assertRedirects(
            response,
            reverse("users:index"),
            fetch_redirect_response=False,
        )

        self.assertTrue(
            User.objects.filter(
                pk=self.author.pk,
            ).exists()
        )

        self.assert_flash_message(
            response,
            "Невозможно удалить пользователя, потому что он используется",
        )
