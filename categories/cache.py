from aiocache.backends.redis import RedisCache
from aiocache.serializers import JsonSerializer


"""Настройки кеша через редис. Используется 2 база данных. Время хранения кеша равно 60 секундам"""


cache = RedisCache(serializer=JsonSerializer(), endpoint='127.0.0.1', port=6379, db=2, ttl=60)
