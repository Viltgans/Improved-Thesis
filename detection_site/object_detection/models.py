from django.conf import settings
from django.db import models


class ImageFeed(models.Model):
    """
    Модель для хранения изображений, загруженных пользователями.

    Атрибуты:
        user (ForeignKey):
            Ссылка на пользователя, загрузившего изображение.
        image (ImageField):
            Исходное изображение.
        ru_processed_image (ImageField):
            Обработанное изображение с русским текстом (может быть пустым).
        en_processed_image (ImageField):
            Обработанное изображение с английским текстом (может быть пустым).
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='images/')
    ru_processed_image = models.ImageField(upload_to='processed_images/', null=True, blank=True)
    en_processed_image = models.ImageField(upload_to='processed_images/', null=True, blank=True)

    def __str__(self):
        """
        Возвращает строковое представление объекта ImageFeed.

        Returns:
            str: Имя пользователя и имя загруженного изображения.
        """
        return f"{self.user.username} - {self.image.name}"


class DetectedObject(models.Model):
    """
    Модель для хранения объектов, обнаруженных на изображении.

    Атрибуты:
        image_feed (ForeignKey):
            Ссылка на объект ImageFeed, к которому относится данный объект.
        ru_object_type (CharField):
            Тип объекта на русском языке.
        en_object_type (CharField):
            Тип объекта на английском языке.
        confidence (FloatField):
            Уверенность в обнаружении объекта (от 0 до 1).
        location (CharField):
            Местоположение объекта на изображении.
    """
    image_feed = models.ForeignKey(ImageFeed, related_name='detected_objects', on_delete=models.CASCADE)
    ru_object_type = models.CharField(max_length=100)
    en_object_type = models.CharField(max_length=100)
    confidence = models.FloatField()
    location = models.CharField(max_length=255)

    def __str__(self):
        """
        Возвращает строковое представление объекта DetectedObject.

        :return: str: Тип объекта и уровень уверенности в процентах,
            а также имя изображения.
        """
        ru_type = self.ru_object_type
        en_type = self.en_object_type
        confidence = f"{self.confidence:.2f}"
        image_name = self.image_feed.image.name

        return f"{ru_type} ({en_type}) - {confidence} - {image_name}"
