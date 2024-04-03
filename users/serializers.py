import datetime
import json

from aiocache.serializers import BaseSerializer


def parse_datetime(val):
    if isinstance(val, datetime.datetime):
        return val.isoformat().replace('+00:00', 'Z')
    pass


class JsonSerializer(BaseSerializer):

    def dumps(self, value):
        return json.dumps(value, default=parse_datetime)

    def loads(self, value):
        if value is None:
            return None
        return json.loads(value)




