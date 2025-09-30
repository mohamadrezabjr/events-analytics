from django.db.models.signals import post_save
from django.dispatch import receiver
from analytics.models import Event
from django_redis import get_redis_connection
@receiver(post_save, sender=Event)
def post_save_event(sender, instance, created, **kwargs):
    con = get_redis_connection('default')
    keys = con.keys('request:*')
    for key in keys:
        con.delete(key)