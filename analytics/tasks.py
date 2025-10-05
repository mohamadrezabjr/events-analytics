from celery import shared_task
from django_redis import get_redis_connection
import hashlib
import json
from datetime import datetime
from django.core.serializers.json import DjangoJSONEncoder
from analytics.models import Event

@shared_task
def create_event(data):
    p_id = data.get('metadata').get('product_id')
    if p_id :
        data['metadata']['product_id'] = str(p_id)
    event = Event.objects.create(**data)


CACHE_LIMIT = 256*1024*1024
@shared_task
def hash_data(data):
    return hashlib.sha256(json.dumps(data, sort_keys = True).encode()).hexdigest()

@shared_task
def save_cache_task(key, data):
    con = get_redis_connection('default')
    info = con.info('memory')
    used_memory = info['used_memory']
    if used_memory > CACHE_LIMIT:
        delete_least_used()

    hashed_key = hash_data(key)
    wrapper = {
        'hits': 1,
        'last_used': datetime.now(),
        'data' : data,
    }

    con.set(f'request:{hashed_key}', json.dumps(wrapper, cls=DjangoJSONEncoder))

@shared_task
def delete_least_used():
    con = get_redis_connection('default')
    keys = con.keys('request:*')
    min_key = None
    min_hits = None
    for key in keys:
        data = con.get(key)
        if data:
            data = json.loads(data)
            if min_hits is None or data.get('hits') <= min_hits:
                min_key = key
                min_hits = data.get('hits')
    if min_key :
        con.delete(min_key)
@shared_task
def delete_cache_keys(pattern):
    con = get_redis_connection('default')
    keys = con.keys(pattern)
    for key in keys:
        con.delete(key)