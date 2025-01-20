"""
URL конфигурация для проекта Django.

Этот файл определяет маршруты URL для административной панели, 
установки языка и включает маршруты приложения object_detection.
"""

from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.views.i18n import set_language

urlpatterns = [
                  # Административная панель
                  path('admin/', admin.site.urls, name='admin'),
                  # Установка языка
                  path('setlang/', set_language, name='set_language'),
                  # Статические файлы медиа
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Добавление маршрутов с поддержкой интернационализации
urlpatterns += i18n_patterns(
    path('', include('object_detection.urls')),  # Включение маршрутов object_detection
)
