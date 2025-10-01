from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from analytics.models import Event
from django_redis import get_redis_connection
from django.core.cache import cache

@receiver([post_save, post_delete], sender=Event)
def post_save_event(sender, instance, created, **kwargs):
    cache.delete_pattern('request:*')
    cache.delete_pattern('*event_list*')
