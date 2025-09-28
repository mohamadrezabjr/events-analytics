from celery import shared_task

from analytics.models import Event
from analytics.serializers import EventSerializer

@shared_task
def create_event(data):
    event = Event.objects.create(**data)
