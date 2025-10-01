from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from analytics.models import Event
from django_redis import get_redis_connection
@receiver(post_save, sender=Event)
def post_save_event(sender, instance, created, **kwargs):
    delete_request_caches()
@receiver(post_delete, sender=Event)
def post_delete_event(sender, instance, **kwargs):
    delete_request_caches()

def delete_request_caches():
    con = get_redis_connection('default')
    keys = con.keys('request:*')
    for key in keys:
        con.delete(key)