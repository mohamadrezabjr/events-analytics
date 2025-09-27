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
class EventSerializer(serializers.Serializer):
    metric = serializers.CharField(required=False, max_length=256)
    user_id = serializers.CharField(required=False, max_length=256)
    session_id = serializers.CharField(required=False, max_length=256)
    from_date = serializers.DateTimeField(required=False)
    to_date = serializers.DateTimeField(required=False)

    #Metadata fields
    device = serializers.CharField(required=False, max_length=256)
    browser = serializers.CharField(required=False, max_length=256)
    page = serializers.CharField(required=False, max_length=256)
    referer = serializers.CharField(required=False, max_length=256)
    product_id = serializers.CharField(required=False, max_length=256)
    product = serializers.CharField(required=False, max_length=256)
    price = serializers.DecimalField(required=False, decimal_places=2, max_digits=10)


    #Group by :
    group_by = serializers.ChoiceField(choices = ['day', 'week', 'month', 'year'], required=False)
    #Agreggate
    aggregate =serializers.ChoiceField(choices = ['sum', 'count', 'avg', 'min', 'max'], required=False)
    field = serializers.ChoiceField(choices=['price','screen_width','screen_height','step'], required=False)

    def validate(self, data):
        if data.get('aggregate') in ['sum', 'avg', 'min', 'max']:
            if not data.get('field'):
                raise serializers.ValidationError(f'For this aggregation ({data.get('aggregate')}), \"Field\" is required')
        return data