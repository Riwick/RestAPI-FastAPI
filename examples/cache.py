from aiocache import RedisCache
from aiocache.serializers import JsonSerializer

cache = RedisCache(serializer=JsonSerializer())
