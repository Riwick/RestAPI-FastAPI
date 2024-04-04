from aiocache import RedisCache

from users.serializers import JsonSerializer


"""Настройки кеша через редис. Используется 3 база данных. Время хранения кеша равно 60 секундам"""


cache = RedisCache(serializer=JsonSerializer(), endpoint='127.0.0.1', port=6379, db=3, ttl=10)
