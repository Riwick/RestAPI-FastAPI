import datetime
import json

from aiocache.serializers import BaseSerializer


"""Тут находятся кастомные сериализаторы для кеширования в редисе"""


def parse_datetime(val):
    """Тут происходит преобразование объекта datetime.datetime в нужную форму для его сериализации"""
    if isinstance(val, datetime.datetime):  # Проверка является ли объект типом datetime.datetime
        return val.isoformat().replace('+00:00', 'Z')  # Переводится в iso format с последующей заменой символов
    pass


class JsonSerializer(BaseSerializer):
    """Сам класс сериализатора, через который происходит сериализация данных в кеш"""

    def dumps(self, value):
        return json.dumps(value, default=parse_datetime)

    def loads(self, value):
        if value is None:
            return None
        return json.loads(value)




