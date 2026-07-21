from django.contrib.auth import SESSION_KEY, get_user_model
from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import reverse


User = get_user_model()

TEST_PASSWORD = "SecurePassword123!"


class UserCRUDTests(TestCase):
    fixtures = ["users.json"]

    def setUp(self):
        self.first_user = User.objects.get(pk=1)
        self.second_user = User.objects.get(pk=2)

    def assert_flash_message(self, response, expected_message):
        response_messages = [
            str(message) for message in get_messages(response.wsgi_request)
        ]

        self.assertIn(
            expected_message,
            response_messages,
        )

    def test_user_list_is_available_without_authentication(self):
        response = self.client.get(
            reverse("users:index"),
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "first_user")
        self.assertContains(response, "second_user")

    def test_user_registration(self):
        response = self.client.post(
            reverse("users:create"),
            {
                "first_name": "Анна",
                "last_name": "Смирнова",
                "username": "anna",
                "password1": TEST_PASSWORD,
                "password2": TEST_PASSWORD,
            },
        )

        self.assertRedirects(
            response,
            reverse("login"),
        )

        self.assertTrue(User.objects.filter(username="anna").exists())

        created_user = User.objects.get(username="anna")

        self.assertTrue(created_user.check_password(TEST_PASSWORD))

        self.assert_flash_message(
            response,
            "Пользователь успешно зарегистрирован",
        )

    def test_duplicate_username_validation(self):
        response = self.client.post(
            reverse("users:create"),
            {
                "first_name": "Другой",
                "last_name": "Пользователь",
                "username": self.first_user.username,
                "password1": TEST_PASSWORD,
                "password2": TEST_PASSWORD,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "уже существует",
        )

    def test_user_can_update_own_account(self):
        self.client.force_login(self.first_user)

        response = self.client.post(
            reverse(
                "users:update",
                kwargs={"pk": self.first_user.pk},
            ),
            {
                "first_name": "Новое имя",
                "last_name": "Новая фамилия",
                "username": "updated_user",
                "password1": TEST_PASSWORD,
                "password2": TEST_PASSWORD,
            },
        )

        self.assertRedirects(
            response,
            reverse("users:index"),
        )

        self.first_user.refresh_from_db()

        self.assertEqual(
            self.first_user.first_name,
            "Новое имя",
        )
        self.assertEqual(
            self.first_user.last_name,
            "Новая фамилия",
        )
        self.assertEqual(
            self.first_user.username,
            "updated_user",
        )
        self.assertTrue(self.first_user.check_password(TEST_PASSWORD))

        self.assert_flash_message(
            response,
            "Пользователь успешно изменен",
        )

    def test_user_cannot_update_another_account(self):
        self.client.force_login(self.first_user)

        old_username = self.second_user.username

        response = self.client.post(
            reverse(
                "users:update",
                kwargs={"pk": self.second_user.pk},
            ),
            {
                "first_name": "Изменённое имя",
                "last_name": "Изменённая фамилия",
                "username": "hacked_user",
                "password1": TEST_PASSWORD,
                "password2": TEST_PASSWORD,
            },
        )

        self.assertRedirects(
            response,
            reverse("users:index"),
        )

        self.second_user.refresh_from_db()

        self.assertEqual(
            self.second_user.username,
            old_username,
        )

        self.assert_flash_message(
            response,
            "У вас нет прав для изменения",
        )

    def test_user_can_delete_own_account(self):
        self.client.force_login(self.first_user)

        response = self.client.post(
            reverse(
                "users:delete",
                kwargs={"pk": self.first_user.pk},
            ),
        )

        self.assertRedirects(
            response,
            reverse("users:index"),
        )

        self.assertFalse(
            User.objects.filter(
                pk=self.first_user.pk,
            ).exists()
        )

        self.assert_flash_message(
            response,
            "Пользователь успешно удален",
        )

    def test_user_cannot_delete_another_account(self):
        self.client.force_login(self.first_user)

        response = self.client.post(
            reverse(
                "users:delete",
                kwargs={"pk": self.second_user.pk},
            ),
        )

        self.assertRedirects(
            response,
            reverse("users:index"),
        )

        self.assertTrue(
            User.objects.filter(
                pk=self.second_user.pk,
            ).exists()
        )

        self.assert_flash_message(
            response,
            "У вас нет прав для изменения",
        )


class AuthenticationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="auth_user",
            first_name="Алексей",
            last_name="Сидоров",
            password=TEST_PASSWORD,
        )

    def assert_flash_message(self, response, expected_message):
        response_messages = [
            str(message) for message in get_messages(response.wsgi_request)
        ]

        self.assertIn(
            expected_message,
            response_messages,
        )

    def test_login(self):
        response = self.client.post(
            reverse("login"),
            {
                "username": self.user.username,
                "password": TEST_PASSWORD,
            },
        )

        self.assertRedirects(
            response,
            reverse("index"),
        )

        self.assertIn(
            SESSION_KEY,
            self.client.session,
        )

        self.assert_flash_message(
            response,
            "Вы залогинены",
        )

    def test_logout_requires_post_and_ends_session(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("logout"),
        )

        self.assertRedirects(
            response,
            reverse("index"),
        )

        self.assertNotIn(
            SESSION_KEY,
            self.client.session,
        )

        self.assert_flash_message(
            response,
            "Вы разлогинены",
        )
