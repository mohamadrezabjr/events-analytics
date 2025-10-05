from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from analytics.models import Event
from analytics.tasks import delete_cache_keys

@receiver(post_delete, sender=Event)
def post_delete_event(sender, instance, **kwargs):
    delete_cache_keys.delay('request:*')
    delete_cache_keys.delay('*event_list*')

@receiver(post_save, sender=Event)
def post_save_event(sender, instance, created, **kwargs):
    delete_cache_keys.delay('request:*')
    delete_cache_keys.delay('*event_list*')

