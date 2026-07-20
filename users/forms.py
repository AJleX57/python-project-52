from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm


User = get_user_model()


class UserForm(UserCreationForm):
    """Форма регистрации и изменения пользователя."""

    first_name = forms.CharField(
        label="Имя",
        max_length=150,
        required=True,
    )
    last_name = forms.CharField(
        label="Фамилия",
        max_length=150,
        required=True,
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = (
            "first_name",
            "last_name",
            "username",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["username"].label = "Имя пользователя"
        self.fields["username"].error_messages["unique"] = (
            "Пользователь с таким именем уже существует."
        )

        self.fields["password1"].label = "Пароль"
        self.fields["password2"].label = "Подтверждение пароля"

        self.order_fields(
            [
                "first_name",
                "last_name",
                "username",
                "password1",
                "password2",
            ]
        )


class LoginForm(AuthenticationForm):
    """Форма входа пользователя."""

    def __init__(self, request=None, *args, **kwargs):
        super().__init__(request=request, *args, **kwargs)

        self.fields["username"].label = "Имя пользователя"
        self.fields["password"].label = "Пароль"
