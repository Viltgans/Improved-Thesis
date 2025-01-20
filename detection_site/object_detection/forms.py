from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User

from .models import ImageFeed


class ImageFeedForm(forms.ModelForm):
    """
    Форма для загрузки изображений в модель ImageFeed.

    Атрибуты:
        image: Изображение для загрузки.
        description: Описание изображения (необязательное).
    """

    class Meta:
        model = ImageFeed
        fields = ['image']
        widgets = {
            'image': forms.ClearableFileInput(
                attrs={
                    'class': 'input__file',
                    'id': 'input__file',
                    'style': 'display: none;',
                    'accept': 'image/*'
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        """
        Инициализация формы.
        Устанавливает метку поля 'image' в False.
        """
        super().__init__(*args, **kwargs)
        self.fields['image'].label = False


class CustomLoginForm(AuthenticationForm):
    """
    Форма для аутентификации пользователя.

    Атрибуты:
        username: Имя пользователя.
        password: Пароль.
    """

    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)


class CustomUserCreationForm(UserCreationForm):
    """
    Форма для регистрации нового пользователя.

    Атрибуты:
        username: Имя пользователя.
        password1: Пароль.
        password2: Подтверждение пароля.
    """

    username = forms.CharField(max_length=150)

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2')
