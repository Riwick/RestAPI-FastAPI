from aiocache import RedisCache

from config import REDIS_HOST, REDIS_PORT, REDIS_TTL
from users.serializers import JsonSerializer


"""Настройки кеша через редис. Используется 3 база данных. Время хранения кеша равно 60 секундам"""


cache = RedisCache(serializer=JsonSerializer(), endpoint=REDIS_HOST, port=REDIS_PORT, db=3, ttl=REDIS_TTL)
