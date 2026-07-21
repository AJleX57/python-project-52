from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import reverse

from labels.models import Label
from statuses.models import Status
from tasks.models import Task


User = get_user_model()


class LabelCRUDTests(TestCase):
    fixtures = ["labels.json"]

    def setUp(self):
        self.user = User.objects.get(
            username="label_user",
        )
        self.status = Status.objects.get(pk=501)
        self.linked_label = Label.objects.get(pk=501)
        self.free_label = Label.objects.get(pk=502)
        self.additional_label = Label.objects.get(pk=503)
        self.task = Task.objects.get(pk=501)

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
            reverse("labels:index"),
            reverse("labels:create"),
            reverse(
                "labels:update",
                kwargs={"pk": self.free_label.pk},
            ),
            reverse(
                "labels:delete",
                kwargs={"pk": self.free_label.pk},
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
                reverse("labels:create"),
                {"name": "Новая метка"},
            ),
            (
                reverse(
                    "labels:update",
                    kwargs={"pk": self.free_label.pk},
                ),
                {"name": "Изменённая метка"},
            ),
            (
                reverse(
                    "labels:delete",
                    kwargs={"pk": self.free_label.pk},
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

    def test_label_list(self):
        self.client.force_login(self.user)

        response = self.client.get(
            reverse("labels:index"),
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            self.linked_label.name,
        )
        self.assertContains(
            response,
            self.free_label.name,
        )
        self.assertContains(
            response,
            "Создать метку",
        )
        self.assertContains(
            response,
            "Изменить",
        )
        self.assertContains(
            response,
            "Удалить",
        )

    def test_label_form_has_standard_field_name(self):
        self.client.force_login(self.user)

        response = self.client.get(
            reverse("labels:create"),
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

    def test_create_label(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("labels:create"),
            {
                "name": "Баг",
            },
        )

        self.assertRedirects(
            response,
            reverse("labels:index"),
            fetch_redirect_response=False,
        )

        self.assertTrue(
            Label.objects.filter(
                name="Баг",
            ).exists()
        )

        self.assert_flash_message(
            response,
            "Метка успешно создана",
        )

    def test_duplicate_label_name(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("labels:create"),
            {
                "name": self.free_label.name,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "уже существует",
        )

        self.assertEqual(
            Label.objects.filter(
                name=self.free_label.name,
            ).count(),
            1,
        )

    def test_update_label(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse(
                "labels:update",
                kwargs={"pk": self.free_label.pk},
            ),
            {
                "name": "Срочная",
            },
        )

        self.assertRedirects(
            response,
            reverse("labels:index"),
            fetch_redirect_response=False,
        )

        self.free_label.refresh_from_db()

        self.assertEqual(
            self.free_label.name,
            "Срочная",
        )

        self.assert_flash_message(
            response,
            "Метка успешно изменена",
        )

    def test_delete_unlinked_label(self):
        self.client.force_login(self.user)

        label_id = self.free_label.pk

        response = self.client.post(
            reverse(
                "labels:delete",
                kwargs={"pk": label_id},
            ),
        )

        self.assertRedirects(
            response,
            reverse("labels:index"),
            fetch_redirect_response=False,
        )

        self.assertFalse(
            Label.objects.filter(
                pk=label_id,
            ).exists()
        )

        self.assert_flash_message(
            response,
            "Метка успешно удалена",
        )

    def test_linked_label_cannot_be_deleted(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse(
                "labels:delete",
                kwargs={"pk": self.linked_label.pk},
            ),
        )

        self.assertRedirects(
            response,
            reverse("labels:index"),
            fetch_redirect_response=False,
        )

        self.assertTrue(
            Label.objects.filter(
                pk=self.linked_label.pk,
            ).exists()
        )

        self.assertTrue(
            self.task.labels.filter(
                pk=self.linked_label.pk,
            ).exists()
        )

        self.assert_flash_message(
            response,
            "Невозможно удалить метку",
        )

    def test_task_form_uses_multiple_label_selection(self):
        self.client.force_login(self.user)

        response = self.client.get(
            reverse("tasks:create"),
        )

        self.assertEqual(response.status_code, 200)

        labels_field = response.context["form"].fields["labels"]

        self.assertTrue(
            labels_field.widget.allow_multiple_selected
        )

        self.assertContains(
            response,
            'name="labels"',
        )
        self.assertContains(
            response,
            'id="id_labels"',
        )
        self.assertContains(
            response,
            "multiple",
        )

    def test_create_task_with_multiple_labels(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("tasks:create"),
            {
                "name": "Задача с несколькими метками",
                "description": "Описание новой задачи",
                "status": self.status.pk,
                "executor": "",
                "labels": [
                    self.free_label.pk,
                    self.additional_label.pk,
                ],
            },
        )

        self.assertRedirects(
            response,
            reverse("tasks:index"),
            fetch_redirect_response=False,
        )

        created_task = Task.objects.get(
            name="Задача с несколькими метками",
        )

        self.assertSetEqual(
            set(
                created_task.labels.values_list(
                    "pk",
                    flat=True,
                )
            ),
            {
                self.free_label.pk,
                self.additional_label.pk,
            },
        )

    def test_update_task_labels(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse(
                "tasks:update",
                kwargs={"pk": self.task.pk},
            ),
            {
                "name": self.task.name,
                "description": self.task.description,
                "status": self.status.pk,
                "executor": "",
                "labels": [
                    self.free_label.pk,
                    self.additional_label.pk,
                ],
            },
        )

        self.assertRedirects(
            response,
            reverse("tasks:index"),
            fetch_redirect_response=False,
        )

        self.task.refresh_from_db()

        self.assertSetEqual(
            set(
                self.task.labels.values_list(
                    "pk",
                    flat=True,
                )
            ),
            {
                self.free_label.pk,
                self.additional_label.pk,
            },
        )
