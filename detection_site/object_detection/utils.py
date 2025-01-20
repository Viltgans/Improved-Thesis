import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from django.core.files.base import ContentFile

from .models import ImageFeed, DetectedObject

# Список меток классов для обнаружения объектов на русском языке
VOC_LABELS_RU = [
    "фон", "самолёт", "велосипед", "птица", "лодка", "бутылка",
    "автобус", "автомобиль", "кошка/кот", "стул", "корова", "стол",
    "собака/пес", "лошадь/конь", "мотоцикл", "человек", "цветок",
    "овца/баран", "диван", "поезд", "телевизор"
]

# Список меток классов для обнаружения объектов на английском языке
VOC_LABELS_EN = [
    "background", "airplane", "bicycle", "bird", "boat", "bottle",
    "bus", "car", "cat", "chair", "cow", "dining table",
    "dog", "horse", "motorbike", "person", "potted plant",
    "sheep", "train", "tv/monitor"
]


def process_image(image_feed_id):
    """
    Обрабатывает изображение, выполняя обнаружение объектов с
    использованием модели MobileNet SSD.

    :param image_feed_id: ID объекта ImageFeed, который необходимо обработать.
    :return: True, если обработка прошла успешно; False в противном случае.
    """
    try:
        # Получение объекта ImageFeed по ID
        image_feed = ImageFeed.objects.get(id=image_feed_id)
        image_path = image_feed.image.path

        # Загрузка модели и конфигурации
        model_path = 'object_detection/mobilenet_iter_73000.caffemodel'
        config_path = 'object_detection/mobilenet_ssd_deploy.prototxt'
        net = cv2.dnn.readNetFromCaffe(config_path, model_path)

        # Чтение изображения
        img = cv2.imread(image_path)
        if img is None:
            print("Не удалось загрузить изображение.")
            return False

        # Преобразование изображения
        h, w = img.shape[:2]
        blob = cv2.dnn.blobFromImage(img, 0.007843, (300, 300), 127.5)

        # Выполнение обнаружения объекта
        net.setInput(blob)
        detections = net.forward()

        for i in range(detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            if confidence > 0.6:
                class_id = int(detections[0, 0, i, 1])
                ru_class_label = VOC_LABELS_RU[class_id]
                en_class_label = VOC_LABELS_EN[class_id]
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                (startX, startY, endX, endY) = box.astype("int")

                # Рисование рамки вокруг обнаруженного объекта
                cv2.rectangle(img, (startX, startY), (endX, endY), (0, 255, 0), 2)

                # Конвертируем его в формат PIL
                ru_img_pil = Image.fromarray(img)
                en_img_pil = Image.fromarray(img)

                # Создаем объект для рисования
                ru_draw = ImageDraw.Draw(ru_img_pil)
                en_draw = ImageDraw.Draw(en_img_pil)

                # Загружаем шрифт с поддержкой кириллицы
                font = ImageFont.truetype("detection_site/font/arial.ttf", 32)

                # Вывод названия класса и уверенности на русском языке
                ru_label = f"{ru_class_label}: {confidence:.2f}"
                en_label = f"{en_class_label}: {confidence:.2f}"

                # Добавляем текст на изображение
                ru_draw.text((startX + 5, startY + 15), ru_label, font=font, fill=(255, 255, 255))
                en_draw.text((startX + 5, startY + 15), en_label, font=font, fill=(255, 255, 255))

                # Конвертируем обратно в формат OpenCV
                ru_img = np.array(ru_img_pil)
                en_img = np.array(en_img_pil)

                # Создание обнаруженного объекта в базе данных
                DetectedObject.objects.create(
                    image_feed=image_feed,
                    ru_object_type=ru_class_label,
                    en_object_type=en_class_label,
                    location=f"{startX},{startY},{endX},{endY}",
                    confidence=float(confidence)
                )

        # Сохранение обработанного изображения
        result, encoded_img = cv2.imencode('.jpg', ru_img)
        if result:
            content = ContentFile(encoded_img.tobytes(), f'processed_{image_feed.image.name}')
            image_feed.ru_processed_image.save(content.name, content, save=True)

        result, encoded_img = cv2.imencode('.jpg', en_img)
        if result:
            content = ContentFile(encoded_img.tobytes(), f'processed_{image_feed.image.name}')
            image_feed.en_processed_image.save(content.name, content, save=True)

        return True

    except ImageFeed.DoesNotExist:
        print("ImageFeed не найден.")
        return False
