from aiocache import RedisCache
from aiocache.serializers import JsonSerializer

cache = RedisCache(serializer=JsonSerializer(), endpoint='127.0.0.1', port=6379, db=1, ttl=60)
