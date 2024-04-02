import json

from aiocache.serializers import BaseSerializer


class JsonSerializer(BaseSerializer):

    def dumps(self, value):
        return json.dumps(value, default=str)

    def loads(self, value):
        if value is None:
            return None
        return json.loads(value)




