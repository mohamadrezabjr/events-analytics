from rest_framework import serializers
from analytics.models import Event


class CreateEventSerializer(serializers.ModelSerializer):
    timestamp = serializers.DateTimeField(source='client_timestamp')
    server_timestamp = serializers.DateTimeField(read_only=True)
    class Meta:
        model = Event
        fields = [
            'event_name',
            'user_id',
            'session_id',
            'timestamp',
            'server_timestamp',
            'metadata'
        ]