"""
Модуль маршрутизации URL для приложения.
"""

from django.urls import path

from . import views

urlpatterns = [
    # Главная страница
    path('', views.home, name='home'),
    # Страница регистрации пользователя
    path('register/', views.register, name='register'),
    # Страница авторизации пользователя
    path('login/', views.user_login, name='login'),
    # Выход из системы
    path('logout/', views.user_logout, name='logout'),
    # Страница пользователя для загрузки изображений и управления ими
    path('dashboard/', views.dashboard, name='dashboard'),
    # Обработка изображения
    path('process/<int:feed_id>/', views.process_image_feed, name='process_feed'),
    # Страница добавления нового изображения
    path('add-image-feed/', views.add_image_feed, name='add_image_feed'),
    # Удаление изображения
    path('image/delete/<int:image_id>/', views.delete_image, name='delete_image'),
]
