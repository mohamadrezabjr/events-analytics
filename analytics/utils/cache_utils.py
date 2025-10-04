from django.core.serializers.json import DjangoJSONEncoder
from django_redis import get_redis_connection
from analytics.tasks import hash_data, save_cache_task
import json
from datetime import datetime

def get_cache(key):
    con = get_redis_connection('default')
    hashed_key = hash_data(key)
    cached = con.get(f'request:{hashed_key}')

    if cached:
        cached = json.loads(cached)
        cached['hits'] += 1
        cached['last_used'] = datetime.now()
        con.set(f'request:{hashed_key}', json.dumps(cached, cls=DjangoJSONEncoder))
        return cached.get('data')
    else:
        return None

def save_cache(key, data):
    if not isinstance(data, dict):
        data = list(data)
    save_cache_task.delay(key, data)
