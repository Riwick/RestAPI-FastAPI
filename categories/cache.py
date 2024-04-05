from aiocache.backends.redis import RedisCache
from aiocache.serializers import JsonSerializer

from config import REDIS_HOST, REDIS_PORT, REDIS_TTL

"""Настройки кеша через редис. Используется 2 база данных. Время хранения кеша равно 60 секундам"""


cache = RedisCache(serializer=JsonSerializer(), endpoint=REDIS_HOST, port=REDIS_PORT, db=2, ttl=REDIS_TTL)
