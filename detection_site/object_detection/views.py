import os

from django.conf import settings
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404

from .forms import ImageFeedForm, CustomLoginForm, CustomUserCreationForm
from .models import ImageFeed
from .utils import process_image


# Отображение главной страницы
def home(request):
    """
    Отображает главную страницу приложения.

    :param request: HTTP-запрос от клиента.
    :return: HttpResponse: Ответ с отрендеренной главной страницей.
    """
    return render(request,
                  'object_detection/home.html',
                  {'clicked': 'home'})


# Отображение страницы регистрации
def register(request):
    """
    Обрабатывает запросы на регистрацию нового пользователя.

    Если метод запроса - POST, проверяет корректность данных формы.
    Если данные валидны и пользователь с таким именем не существует,
    сохраняет нового пользователя и выполняет его авторизацию.
    В противном случае отображает форму регистрации.

    :param request: HTTP-запрос от клиента.
    :return: HttpResponse: Ответ с формой регистрации или перенаправление
        на страницу панели управления после успешной регистрации.
    """
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password1 = form.cleaned_data['password1']
            password2 = form.cleaned_data['password2']

            # Проверка на совпадение паролей
            if password1 != password2:
                form.errors()
            else:
                # Проверка на уникальность username
                if User.objects.filter(username=username).exists():
                    form.errors()
                else:
                    user = form.save()  # Сохраняем пользователя
                    login(request, user)  # Авторизуем пользователя
                    return redirect('dashboard')
    else:
        # Иначе отображаем форму регистрации
        form = CustomUserCreationForm()

    return render(request,
                  'object_detection/register.html',
                  {'form': form, 'clicked': 'register'})


# Отображение страницы авторизации
def user_login(request):
    """
    Обрабатывает запрос на вход пользователя.

    :param request: HTTP-запрос от клиента.
    :return: HttpResponse: Ответ с формой входа или
        перенаправление на страницу панели управления.
    """
    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')
            else:
                form.errors()
    else:
        form = CustomLoginForm()

    return render(request,
                  'object_detection/login.html',
                  {'form': form, 'clicked': 'login'})


# Логика выхода из системы с перенаправлением на главную страницу
@login_required
def user_logout(request):
    """
    Выход пользователя из системы.

    Этот метод завершает сессию пользователя и
    перенаправляет на главную страницу сайта.
    Доступно только для авторизованных пользователей.

    :param request: HTTP-запрос от клиента.
    :return: HttpResponseRedirect: Перенаправление на главную страницу.
    """
    logout(request)
    return redirect('home')


# Отображение страницы личной панели управления пользователя
@login_required
def dashboard(request):
    """
    Отображение страницы личной панели пользователя.

    Проверяет авторизацию пользователя.
    При отсутствии авторизации перенаправляет на страницу авторизации.
    При авторизации отображает панель управления с изображениями пользователя.

    :param request: HTTP-запрос от клиента.
    :return: HttpResponse: Ответ с отрендеренной страницей личной панели пользователя
        или перенаправление на страницу авторизации.
    """

    # Проверка на авторизацию пользователя с последующим перенаправлением на страницу авторизации
    if not request.user.is_authenticated:
        # Для корректного перенаправления на страницу авторизации используем функцию redirect
        return redirect('/accounts/login/%s?next=%s' % (settings.LOGIN_URL, request.path),
                        {'clicked': 'login'})

    # Получаем изображения, связанные с текущим пользователем
    image_feeds = ImageFeed.objects.filter(user=request.user)

    # Отображаем страницу личной панели пользователя с изображениями
    return render(request,
                  'object_detection/dashboard.html',
                  {'image_feeds': image_feeds, 'clicked': 'dashboard'})


# Обработка потока изображений
@login_required
def process_image_feed(request, feed_id):
    """
    Обрабатывает поток изображений для заданного идентификатора.

    :param request: HTTP-запрос от клиента.
    :param feed_id: Идентификатор потока изображений (int).
    :return: HttpResponseRedirect: Перенаправление на страницу панели управления.
    """
    image_feed = get_object_or_404(ImageFeed, id=feed_id, user=request.user)
    process_image(feed_id)
    return redirect('dashboard')


# Отображение страницы добавления изображения в базу данных c обработкой
@login_required
def add_image_feed(request):
    """
    Отображение страницы добавления изображения в базу данных с обработкой.

    Если метод запроса - POST, проверяет корректность данных формы.
    Если форма валидна, сохраняет изображение с указанием владельца.
    В противном случае отображает пустую форму.

    :param request: HTTP-запрос от клиента.
    :return: HttpResponse: Ответ с отрендеренной страницей или
        перенаправление на страницу добавления изображения.
    """
    if request.method == 'POST':
        form = ImageFeedForm(request.POST, request.FILES)
        if form.is_valid():
            # Сохранение изображения в базу данных с указанием владельца, если форма валидна
            image_feed = form.save(commit=False)
            image_feed.user = request.user
            image_feed.save()
            return redirect('dashboard')
    else:
        # Иначе отображаем форму добавления изображения
        form = ImageFeedForm()

    return render(request,
                  'object_detection/add_image_feed.html',
                  {'form': form})


@login_required
def delete_image(request, image_id):
    """
    Удаляет изображение, если пользователь является его владельцем.
    Удаляет файлы изображения и обработанного изображения из файловой системы.

    :param request: HTTP-запрос от клиента.
    :param image_id: ID изображения, которое нужно удалить
    :return: HttpResponseRedirect: Перенаправление на страницу
        панели управления после удаления изображения.
    """
    # Проверка на удаление изображения только его владельцем
    image = get_object_or_404(ImageFeed, id=image_id, user=request.user)

    # Получение путей к файлам изображения и обработанного изображения
    image_path = os.path.join(settings.MEDIA_ROOT, image.image.name)
    ru_processed_image_path = os.path.join(settings.MEDIA_ROOT, image.ru_processed_image.name)
    en_processed_image_path = os.path.join(settings.MEDIA_ROOT, image.en_processed_image.name)

    # Удаляем объект из базы данных
    image.delete()

    # Удаляем файлы, если они существуют
    if os.path.exists(image_path):
        try:
            os.remove(image_path)
        except Exception as e:
            print(f"Ошибка при удалении файла {image_path}: {e}")

    if os.path.exists(ru_processed_image_path):
        try:
            os.remove(ru_processed_image_path)
        except Exception as e:
            print(f"Ошибка при удалении файла {ru_processed_image_path}: {e}")

    if os.path.exists(en_processed_image_path):
        try:
            os.remove(en_processed_image_path)
        except Exception as e:
            print(f"Ошибка при удалении файла {en_processed_image_path}: {e}")
    return redirect('dashboard')
